#!/usr/bin/env python3
"""treiber.py — faehrt den Handoff-Zyklus von AUSSEN, damit niemand daneben sitzen muss.

Das Problem: ein Waechter kann `/clear` und `/resume` nicht ausloesen — das sind Befehle
des Programms selbst. Ohne Treiber schreibt eine Sitzung an der Kontext-Grenze bestenfalls
den Handoff-Brief und hoert auf; den Neustart macht der Mensch. Dieses Skript uebernimmt
genau diesen Neustart: es startet headless Sitzungen (`claude -p`) nacheinander, erkennt
das Sitzungs-Ende und reicht den Brief an eine frische Sitzung weiter — beliebig oft,
bis der Auftrag fertig ist oder ein Abbruch-Kriterium greift. Hintergrund und
Entscheidungen: `KONZEPT.md`, Kern-Entscheidungen 4 und 5.

    python treiber.py auto "<auftrag>" [--projekt PFAD] [--max-runden N] [--modell M]
    python treiber.py status   [--projekt PFAD]
    python treiber.py stopp    [--projekt PFAD]     # Not-Aus: wirkt vor der naechsten Runde

Mechanik (synchroner Loop, bewusst keine Staffel wie das curaops-Vorbild):

1. Runde 1 bekommt den Auftrag plus Treiber-Vertrag; jede Sitzung laeuft mit
   `SCRATCHPAD_AUTO_HANDOFF=1`, der Kontext-Waechter erzwingt also den Brief.
2. Der Treiber WARTET auf das Prozess-Ende (deshalb gibt es nie ein "altes Fenster"
   zu schliessen — alle Sitzungen laufen nacheinander im einen Treiber-Fenster).
3. Liegt danach `state/treiber-fertig`: sauberes Ende. Sonst: frische Sitzung mit dem
   Resume-Auftrag (Brief lesen, gegen den Arbeitsbaum pruefen, weitermachen).

Ende-Erkennung, nur Dateien und Exit-Codes (nichts Geratenes):
`treiber-fertig` (Sitzung meldet fertig) · `treiber-stopp` (Not-Aus des Menschen, auch
per `python treiber.py stopp` aus einem zweiten Terminal) · Brief-Hash zweimal in Folge
unveraendert (Stillstand) · Exit != 0 zweimal in Folge (Fehler) · Runden-Obergrenze
(Default 40) · Strg+C im Treiber-Fenster.

SICHERHEIT: die Sitzungen laufen mit `--dangerously-skip-permissions` — sie fragen NIE
nach Freigaben und duerfen alles, was das Konto darf. Nur in Umgebungen fahren, in denen
das vertretbar ist (eigener Branch/Worktree, kein Produktiv-Zugriff). Details: README.md.

Nur Standardbibliothek, laeuft ab Python 3.9 (dieselbe Basis wie die Waechter).
"""
from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import time
from collections import namedtuple

# ── Konstanten ────────────────────────────────────────────────────────────────
AGENTEN_ORDNER = ".claude"           # per --agenten-ordner ueberschreibbar
BRIEF_NAME = "handoff-brief.md"
FERTIG_NAME = "treiber-fertig"       # legt die SITZUNG an, wenn der Auftrag fertig ist
STOPP_NAME = "treiber-stopp"         # legt der MENSCH an (Not-Aus)
MARKER_NAME = "treiber-aktiv"        # legt der TREIBER an; der Kontext-Waechter liest ihn
LOG_NAME = "treiber.log"

DEFAULT_MAX_RUNDEN = 40              # Kosten-Deckel; 0 = unbegrenzt (bewusste Ansage)
DEFAULT_STILLSTAND = 2               # Runden ohne Brief-Aenderung bis zum Abbruch
DEFAULT_FEHLER = 2                   # Exit != 0 in Folge bis zum Abbruch
DEFAULT_MODELL = "opus"
DEFAULT_BUDGET = 150_000             # Kontext-Schwelle der Sitzungen (Waechter-Default)

ENV_CLAUDE_BIN = "SCRATCHPAD_CLAUDE_BIN"

Ergebnis = namedtuple("Ergebnis", "grund runden")

# ── Prompts ───────────────────────────────────────────────────────────────────
# Der Vertrag, den JEDE Sitzung des Laufs traegt. Er ist die einzige Stelle, an der
# einer unbeaufsichtigten Sitzung gesagt wird, wie sie endet und was sie nie tut.
VERTRAG = """
So laeuft dieser Lauf (verbindlich):

1. Du laeufst UNBEAUFSICHTIGT. Niemand beantwortet Fragen. Braucht etwas eine
   Entscheidung des Users, park sie als offenen Punkt im Handoff-Brief und arbeite am
   naechsten Punkt weiter.
2. Blockt der Kontext-Waechter dein Turn-Ende (Meldung "[Kontext-Budget]"), ist deine
   Runde zu Ende — nicht deine Arbeit. Schreibe den Stand destilliert als Handoff-Brief
   nach `{brief}` (was erledigt ist, was offen ist, wo du genau stehst, Belege und
   Pfade fuer den Nachfolger) und beende dann deinen Turn. Der Treiber startet
   automatisch eine frische Sitzung, die den Brief liest.
3. Ist der Auftrag FERTIG — oder geht es nur noch mit einer User-Entscheidung weiter —,
   schreibe den Abschluss-Stand nach `{brief}`, lege danach die Datei `{fertig}` an
   (eine Zeile: warum der Lauf endet) und beende deinen Turn.
4. Du fuehrst NIEMALS `git push` aus. Committen ja, pushen nie.
""".strip()

START_PROMPT = """
Du bist die erste Sitzung eines unbeaufsichtigten Treiber-Laufs.

AUFTRAG:
{auftrag}

{vertrag}
""".strip()

RESUME_PROMPT = """
Du bist Runde {runde} eines unbeaufsichtigten Treiber-Laufs. Dein Vorgaenger hat sein
Kontext-Budget aufgebraucht — er ist NICHT gescheitert, seine Arbeit steht im
Arbeitsbaum.

Lies zuerst `{brief}` und pruefe die Kernpunkte gegen den Arbeitsbaum (der Brief ist
ein Bericht, kein Beweis; bei Widerspruch gewinnt der Arbeitsbaum). Mach dann beim
ersten offenen Punkt weiter. Fang nichts blind neu an und nimm nichts zurueck, was
bereits richtig ist.

{vertrag}
""".strip()


# ── Kommando-Bau (der einzige Beruehrpunkt mit dem echten CLI) ────────────────
def build_kommando(prompt: str, modell: str, claude_bin: str) -> list:
    """Das headless Sitzungs-Kommando. `--dangerously-skip-permissions` ist Pflicht:
    eine unbeaufsichtigte Sitzung kann keine Freigabe-Fragen beantworten, und Schreiben
    unter den Agenten-Ordner gilt als sensitive file, was auch Allow-Regeln nicht
    aufheben (im curaops-Vorbild gemessen)."""
    return [
        claude_bin, "-p", prompt,
        "--dangerously-skip-permissions",
        "--model", modell,
    ]


class Treiber:
    """Der Zyklus: Sitzung starten → Ende abwarten → Signale lesen → naechste Runde.

    Der Prozess-Start ist als `starter(prompt, env) -> exit_code` injizierbar, damit der
    Treiber ohne echte Claude-Sitzungen testbar ist. Der echte Starter (`_echter_start`)
    ist bewusst duenn: Kommando bauen, Ausgabe in die Log-Datei, auf das Ende warten.
    """

    def __init__(self, projekt, auftrag, starter=None, max_runden=DEFAULT_MAX_RUNDEN,
                 stillstand_limit=DEFAULT_STILLSTAND, fehler_limit=DEFAULT_FEHLER,
                 modell=DEFAULT_MODELL, budget=DEFAULT_BUDGET,
                 agenten_ordner=AGENTEN_ORDNER, claude_bin=None, log=None):
        self.projekt = os.path.abspath(projekt)
        self.auftrag = auftrag
        self.starter = starter or self._echter_start
        self.max_runden = max_runden
        self.stillstand_limit = stillstand_limit
        self.fehler_limit = fehler_limit
        self.modell = modell
        self.budget = budget
        self.state_dir = os.path.join(self.projekt, agenten_ordner, "state")
        self.claude_bin = claude_bin or os.environ.get(ENV_CLAUDE_BIN, "claude")
        self._log = log if log is not None else self._log_default

    # -- Pfade -----------------------------------------------------------------
    def _pfad(self, name):
        return os.path.join(self.state_dir, name)

    @property
    def brief(self):
        return self._pfad(BRIEF_NAME)

    # -- Log -------------------------------------------------------------------
    def _log_default(self, msg):
        zeile = "[%s] %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
        print(zeile, flush=True)
        try:
            os.makedirs(self.state_dir, exist_ok=True)
            with open(self._pfad(LOG_NAME), "a", encoding="utf-8") as fh:
                fh.write(zeile + "\n")
        except OSError:
            pass  # Log ist Komfort, nie Abbruchgrund

    # -- Signale ---------------------------------------------------------------
    def _brief_hash(self):
        try:
            with open(self.brief, "rb") as fh:
                return hashlib.sha256(fh.read()).hexdigest()
        except OSError:
            return None

    def _existiert(self, name):
        return os.path.isfile(self._pfad(name))

    def _raeume(self, name):
        try:
            os.remove(self._pfad(name))
        except OSError:
            pass

    # -- Prompts ---------------------------------------------------------------
    def _vertrag(self):
        brief_rel = self.brief.replace("\\", "/")
        return VERTRAG.format(brief=brief_rel,
                              fertig=self._pfad(FERTIG_NAME).replace("\\", "/"))

    def _prompt(self, runde):
        # Massgeblich ist der BRIEF, nicht die Rundenzahl: ist Runde 1 ohne Brief
        # abgestuerzt, startet die Wiederholung wieder mit dem Auftrag — ein
        # Resume-Prompt ohne Brief liefe ins Leere.
        if self._brief_hash() is None:
            return START_PROMPT.format(auftrag=self.auftrag.strip(), vertrag=self._vertrag())
        return RESUME_PROMPT.format(runde=runde, brief=self.brief.replace("\\", "/"),
                                    vertrag=self._vertrag())

    # -- Sitzungs-Start (echt) -------------------------------------------------
    def _echter_start(self, prompt, env):
        cmd = build_kommando(prompt, self.modell, self.claude_bin)
        os.makedirs(self.state_dir, exist_ok=True)
        with open(self._pfad(LOG_NAME), "a", encoding="utf-8") as log:
            proc = subprocess.run(cmd, cwd=self.projekt, env=env,
                                  stdin=subprocess.DEVNULL, stdout=log,
                                  stderr=subprocess.STDOUT)
        return proc.returncode

    def _umgebung(self):
        env = dict(os.environ)
        env["SCRATCHPAD_AUTO_HANDOFF"] = "1"      # der Waechter erzwingt den Brief
        env["SCRATCHPAD_KONTEXT_BUDGET"] = str(self.budget)
        # Abo-Login: ein gesetzter API-Key wuerde die Sitzungen ueber die API abrechnen.
        env.pop("ANTHROPIC_API_KEY", None)
        return env

    # -- Der Zyklus ------------------------------------------------------------
    def lauf(self) -> Ergebnis:
        os.makedirs(self.state_dir, exist_ok=True)
        # Alt-Signale eines frueheren Laufs raeumen: eine liegengebliebene Fertig- oder
        # Stopp-Datei wuerde den frischen Lauf sofort und faelschlich beenden.
        for name in (FERTIG_NAME, STOPP_NAME):
            if self._existiert(name):
                self._log("Raeume Alt-Signal %s aus einem frueheren Lauf weg." % name)
                self._raeume(name)

        runde = 0
        stillstand = 0
        fehler = 0
        letzter_hash = self._brief_hash()
        grund = "runden-limit"

        # Marker fuer den Kontext-Waechter: solange er liegt, nennt dessen Meldung den
        # Treiber-Weg (Brief schreiben, Turn beenden) statt /clear + /resume.
        with open(self._pfad(MARKER_NAME), "w", encoding="utf-8") as fh:
            fh.write(time.strftime("%Y-%m-%d %H:%M:%S") + "\n")
        try:
            while self.max_runden <= 0 or runde < self.max_runden:
                if self._existiert(STOPP_NAME):
                    grund = "stopp"
                    break
                runde += 1
                self._log("Runde %d startet (Modell %s, Budget %d)."
                          % (runde, self.modell, self.budget))
                rc = self.starter(self._prompt(runde), self._umgebung())

                if self._existiert(FERTIG_NAME):
                    grund = "fertig"
                    break
                if self._existiert(STOPP_NAME):
                    grund = "stopp"
                    break
                if rc != 0:
                    fehler += 1
                    self._log("Runde %d endete mit Exit %d (%d/%d Fehler in Folge)."
                              % (runde, rc, fehler, self.fehler_limit))
                    if fehler >= self.fehler_limit:
                        grund = "fehler"
                        break
                    continue
                fehler = 0

                h = self._brief_hash()
                if h == letzter_hash:
                    stillstand += 1
                    self._log("Runde %d ohne Brief-Aenderung (%d/%d)."
                              % (runde, stillstand, self.stillstand_limit))
                    if stillstand >= self.stillstand_limit:
                        grund = "stillstand"
                        break
                else:
                    stillstand = 0
                    letzter_hash = h
        finally:
            self._raeume(MARKER_NAME)

        self._log("Lauf beendet nach %d Runde(n): %s." % (runde, grund))
        return Ergebnis(grund=grund, runden=runde)


# ── CLI ───────────────────────────────────────────────────────────────────────
def build_parser():
    p = argparse.ArgumentParser(
        prog="treiber.py",
        description="Faehrt den Handoff-Zyklus unbeaufsichtigt: Sitzung -> Brief -> "
                    "frische Sitzung, bis fertig oder ein Abbruch-Kriterium greift.")
    sub = p.add_subparsers(dest="befehl", required=True)

    auto = sub.add_parser("auto", help="Lauf starten und bis zum Ende fahren")
    auto.add_argument("auftrag", help="der Auftrag der ersten Sitzung")
    auto.add_argument("--max-runden", type=int, default=DEFAULT_MAX_RUNDEN,
                      help="Obergrenze (Default %d; 0 = unbegrenzt, bewusste Ansage)"
                           % DEFAULT_MAX_RUNDEN)
    auto.add_argument("--modell", default=DEFAULT_MODELL,
                      help="Modell der Sitzungen (Default: %s)" % DEFAULT_MODELL)
    auto.add_argument("--budget", type=int, default=DEFAULT_BUDGET,
                      help="Kontext-Schwelle je Sitzung (Default %d)" % DEFAULT_BUDGET)
    auto.add_argument("--claude", dest="claude_bin", default=None,
                      help="Pfad zum claude-CLI (Default: 'claude' bzw. %s)" % ENV_CLAUDE_BIN)

    sub.add_parser("status", help="eine Zeile Stand (Signale, Brief-Alter)")
    sub.add_parser("stopp", help="Not-Aus: Stopp-Datei anlegen, wirkt vor der naechsten Runde")

    for name, parser in sub.choices.items():
        parser.add_argument("--projekt", default=".", help="Projekt-Wurzel (Default: cwd)")
        parser.add_argument("--agenten-ordner", default=AGENTEN_ORDNER,
                            help="Name des Agenten-Ordners (Default: %s)" % AGENTEN_ORDNER)
    return p


def cmd_status(state_dir):
    def alter(pfad):
        try:
            minuten = int((time.time() - os.path.getmtime(pfad)) // 60)
            return "vor %d min" % minuten
        except OSError:
            return "fehlt"
    print("Treiber: Marker %s | Brief %s | fertig %s | stopp %s" % (
        "liegt" if os.path.isfile(os.path.join(state_dir, MARKER_NAME)) else "fehlt",
        alter(os.path.join(state_dir, BRIEF_NAME)),
        alter(os.path.join(state_dir, FERTIG_NAME)),
        alter(os.path.join(state_dir, STOPP_NAME))), flush=True)
    return 0


def cmd_stopp(state_dir):
    os.makedirs(state_dir, exist_ok=True)
    with open(os.path.join(state_dir, STOPP_NAME), "w", encoding="utf-8") as fh:
        fh.write("Not-Aus %s\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
    print("Stopp-Datei gelegt — der Treiber beendet den Lauf vor der naechsten Runde. "
          "Die laufende Sitzung wird nicht getoetet; sie darf ihren Brief zu Ende "
          "schreiben.", flush=True)
    return 0


def main(argv=None):
    args = build_parser().parse_args(argv)
    state_dir = os.path.join(os.path.abspath(args.projekt), args.agenten_ordner, "state")
    if args.befehl == "status":
        return cmd_status(state_dir)
    if args.befehl == "stopp":
        return cmd_stopp(state_dir)

    treiber = Treiber(projekt=args.projekt, auftrag=args.auftrag,
                      max_runden=args.max_runden, modell=args.modell,
                      budget=args.budget, agenten_ordner=args.agenten_ordner,
                      claude_bin=args.claude_bin)
    ergebnis = treiber.lauf()
    return 0 if ergebnis.grund in ("fertig", "stopp") else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nAbgebrochen (Strg+C). Laufende Sitzung endet mit dem Treiber; "
              "der letzte Brief liegt im state-Ordner.", flush=True)
        sys.exit(130)
