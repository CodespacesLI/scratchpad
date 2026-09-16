#!/usr/bin/env python3
"""Selbsttest fuer treiber.py — Aufruf: `python test_treiber.py`.

Reine asserts, kein Test-Framework (gleicher Runner-Stil wie die Waechter-Tests in
`hooks/`). Der Treiber wird OHNE echte Claude-Sitzungen getestet: der Prozess-Start ist
als `starter`-Funktion injizierbar; die Fakes hier simulieren, was eine Sitzung auf der
Platte hinterlaesst (Handoff-Brief, Fertig-Datei, Stopp-Datei) und welchen Exit-Code sie
liefert.

Abgedeckt: Fertig-Signal, Resume-Prompt ab Runde 2, Not-Aus (Stopp-Datei),
Stillstand-Erkennung (Brief-Hash unveraendert), Fehler-Abbruch (Exit != 0),
Runden-Obergrenze, Marker-Lebenszyklus, Alt-Signale werden beim Start geraeumt,
Umgebung der Sitzung (Auto-Handoff-Schalter), Kommando-Bau des echten Starters.
"""
from __future__ import annotations

import os
import sys
import tempfile

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)

import treiber  # noqa: E402

FEHLER = []


def check(name, bedingung, detail=""):
    status = "ok" if bedingung else "FEHLT"
    print("  [%s] %s%s" % (status, name, (" — " + detail) if (detail and not bedingung) else ""))
    if not bedingung:
        FEHLER.append(name)


def neuer_treiber(projekt, starter, **kw):
    kw.setdefault("max_runden", 10)
    return treiber.Treiber(projekt=projekt, auftrag="Baue das Feature X fertig.",
                           starter=starter, log=lambda *_: None, **kw)


def state_pfad(projekt, name):
    return os.path.join(projekt, ".claude", "state", name)


def schreibe(pfad, inhalt):
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    with open(pfad, "w", encoding="utf-8") as fh:
        fh.write(inhalt)


def test_fertig_in_runde_1():
    print("Fertig-Signal beendet den Lauf sauber:")
    with tempfile.TemporaryDirectory() as projekt:
        marker_gesehen = []

        def starter(prompt, env):
            marker_gesehen.append(os.path.isfile(state_pfad(projekt, "treiber-aktiv")))
            schreibe(state_pfad(projekt, "treiber-fertig"), "Auftrag fertig.")
            return 0

        ergebnis = neuer_treiber(projekt, starter).lauf()
        check("grund ist 'fertig'", ergebnis.grund == "fertig", repr(ergebnis.grund))
        check("genau 1 Runde", ergebnis.runden == 1, repr(ergebnis.runden))
        check("Marker lag waehrend der Sitzung", marker_gesehen == [True])
        check("Marker nach dem Lauf weggeraeumt",
              not os.path.isfile(state_pfad(projekt, "treiber-aktiv")))


def test_resume_prompt_ab_runde_2():
    print("Runde 1 traegt den Auftrag, Runde 2 den Brief-Verweis:")
    with tempfile.TemporaryDirectory() as projekt:
        prompts = []

        def starter(prompt, env):
            prompts.append(prompt)
            schreibe(state_pfad(projekt, "handoff-brief.md"), "Stand Runde %d" % len(prompts))
            if len(prompts) == 2:
                schreibe(state_pfad(projekt, "treiber-fertig"), "fertig")
            return 0

        ergebnis = neuer_treiber(projekt, starter).lauf()
        check("2 Runden gelaufen", ergebnis.runden == 2, repr(ergebnis.runden))
        check("Runde 1 nennt den Auftrag", "Feature X" in prompts[0])
        check("Runde 2 nennt den Handoff-Brief", "handoff-brief.md" in prompts[1])
        check("Runde 2 verlangt Pruefung gegen den Arbeitsbaum",
              "Arbeitsbaum" in prompts[1] or "pruefe" in prompts[1].lower())
        check("jede Runde traegt den Vertrag (kein git push)",
              all("git push" in p for p in prompts))


def test_not_aus_stoppdatei():
    print("Not-Aus: die Stopp-Datei bricht vor der naechsten Runde ab:")
    with tempfile.TemporaryDirectory() as projekt:
        def starter(prompt, env):
            schreibe(state_pfad(projekt, "handoff-brief.md"), "Stand")
            schreibe(state_pfad(projekt, "treiber-stopp"), "")
            return 0

        ergebnis = neuer_treiber(projekt, starter).lauf()
        check("grund ist 'stopp'", ergebnis.grund == "stopp", repr(ergebnis.grund))
        check("genau 1 Runde", ergebnis.runden == 1, repr(ergebnis.runden))


def test_stillstand_brief_unveraendert():
    print("Stillstand: unveraenderter Brief zweimal in Folge bricht ab:")
    with tempfile.TemporaryDirectory() as projekt:
        def starter(prompt, env):
            schreibe(state_pfad(projekt, "handoff-brief.md"), "immer derselbe Stand")
            return 0

        ergebnis = neuer_treiber(projekt, starter).lauf()
        check("grund ist 'stillstand'", ergebnis.grund == "stillstand", repr(ergebnis.grund))
        check("3 Runden (1 Fortschritt + 2 ohne)", ergebnis.runden == 3, repr(ergebnis.runden))


def test_fehler_abbruch():
    print("Fehler: zweimal Exit != 0 in Folge bricht ab:")
    with tempfile.TemporaryDirectory() as projekt:
        prompts = []

        def starter(prompt, env):
            prompts.append(prompt)
            return 1

        ergebnis = neuer_treiber(projekt, starter).lauf()
        check("grund ist 'fehler'", ergebnis.grund == "fehler", repr(ergebnis.grund))
        check("2 Runden", ergebnis.runden == 2, repr(ergebnis.runden))
        check("ohne Brief startet Runde 2 wieder mit dem Auftrag",
              len(prompts) == 2 and "Feature X" in prompts[1])


def test_runden_limit():
    print("Runden-Obergrenze deckelt den Lauf:")
    with tempfile.TemporaryDirectory() as projekt:
        zaehler = [0]

        def starter(prompt, env):
            zaehler[0] += 1
            schreibe(state_pfad(projekt, "handoff-brief.md"), "Stand %d" % zaehler[0])
            return 0

        ergebnis = neuer_treiber(projekt, starter, max_runden=3).lauf()
        check("grund ist 'runden-limit'", ergebnis.grund == "runden-limit", repr(ergebnis.grund))
        check("genau 3 Runden", ergebnis.runden == 3, repr(ergebnis.runden))


def test_alt_signale_werden_geraeumt():
    print("Alte Fertig-/Stopp-Dateien blockieren keinen frischen Start:")
    with tempfile.TemporaryDirectory() as projekt:
        schreibe(state_pfad(projekt, "treiber-fertig"), "alt")
        schreibe(state_pfad(projekt, "treiber-stopp"), "alt")
        runden = [0]

        def starter(prompt, env):
            runden[0] += 1
            schreibe(state_pfad(projekt, "handoff-brief.md"), "Stand %d" % runden[0])
            if runden[0] == 2:
                schreibe(state_pfad(projekt, "treiber-fertig"), "jetzt wirklich")
            return 0

        ergebnis = neuer_treiber(projekt, starter).lauf()
        check("Lauf lief trotz Alt-Signalen 2 Runden",
              ergebnis.grund == "fertig" and ergebnis.runden == 2,
              "%s/%s" % (ergebnis.grund, ergebnis.runden))


def test_sitzungs_umgebung():
    print("Die Sitzung bekommt Auto-Handoff und Budget in die Umgebung:")
    with tempfile.TemporaryDirectory() as projekt:
        umgebungen = []

        def starter(prompt, env):
            umgebungen.append(dict(env))
            schreibe(state_pfad(projekt, "treiber-fertig"), "fertig")
            return 0

        neuer_treiber(projekt, starter, budget=99000).lauf()
        env = umgebungen[0]
        check("SCRATCHPAD_AUTO_HANDOFF=1", env.get("SCRATCHPAD_AUTO_HANDOFF") == "1")
        check("SCRATCHPAD_KONTEXT_BUDGET gesetzt", env.get("SCRATCHPAD_KONTEXT_BUDGET") == "99000")


def test_kommando_bau():
    print("Der echte Starter baut das claude-Kommando ohne Freigabe-Fragen:")
    cmd = treiber.build_kommando("mein prompt", modell="opus", claude_bin="claude")
    check("headless (-p) mit Prompt", "-p" in cmd and "mein prompt" in cmd)
    check("Freigaben abgeschaltet", "--dangerously-skip-permissions" in cmd)
    check("Modell gesetzt", "--model" in cmd and "opus" in cmd)


def test_fehlendes_cli():
    print("Fehlt das claude-CLI, meldet der Starter Exit 127 statt abzustuerzen:")
    with tempfile.TemporaryDirectory() as projekt:
        t = treiber.Treiber(projekt, "x", claude_bin="gibt-es-nicht-scratchpad",
                            log=lambda msg: None)
        check("Exit 127", t._echter_start("prompt", dict(os.environ)) == 127)


def test_cli_parser():
    print("CLI: auto/status/stopp werden geparst:")
    p = treiber.build_parser()
    args = p.parse_args(["auto", "bau das", "--max-runden", "5"])
    check("auto-Auftrag", args.befehl == "auto" and args.auftrag == "bau das")
    check("max-runden", args.max_runden == 5)
    args2 = p.parse_args(["stopp"])
    check("stopp-Befehl", args2.befehl == "stopp")


def main():
    for test in (test_fertig_in_runde_1, test_resume_prompt_ab_runde_2,
                 test_not_aus_stoppdatei, test_stillstand_brief_unveraendert,
                 test_fehler_abbruch, test_runden_limit,
                 test_alt_signale_werden_geraeumt, test_sitzungs_umgebung,
                 test_kommando_bau, test_fehlendes_cli, test_cli_parser):
        test()
    if FEHLER:
        print("\nFEHLGESCHLAGEN: %d Pruefung(en): %s" % (len(FEHLER), ", ".join(FEHLER)))
        return 1
    print("\nAlle Treiber-Pruefungen bestanden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
