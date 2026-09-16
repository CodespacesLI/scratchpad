#!/usr/bin/env python3
"""Traegt Harness-Eintraege in eine settings.json ein — per JSON-Merge.

Aufruf: python install_settings.py <settings.json> <style-name>
                                   [<hooks-quelle.json> <agentenordner>]

Bewusst ein echter JSON-Merge statt eines String-Splice am ersten "{": ein
Splice erzeugt an abweichend formatierten Dateien ungueltiges JSON (aus "{}"
wird "{\n  \"outputStyle\": \"x\",}" — Komma vor der Klammer). Und bewusst ein
Merge statt eines Ueberschreibens der ganzen Datei: das Zielprojekt hat
moeglicherweise schon eigene Settings (permissions, env, eigene Hooks), die ein
stumpfes Kopieren von agent/settings-hooks.json ersatzlos vernichten wuerde.
Beide Installer (Bash und PowerShell) rufen diesen einen Helfer auf, damit ihre
Ergebnisse byte-identisch sind; er wird NICHT ins Zielprojekt kopiert.

Werden Hooks-Quelle und Agentenordner mitgegeben, wandern auch die Hook-
Eintraege und die Statuszeile (`statusLine`) des Harness in den Merge. Der Platzhalter <AGENTENORDNER> wird dabei
VOR dem Vergleich ersetzt: der Installer ersetzt ihn erst nach diesem Schritt,
also stuende beim zweiten Lauf in der Zieldatei der fertige Pfad und in der
Quelle noch der Platzhalter — jeder Hook waere doppelt eingetragen.

Idempotent: ein bereits vorhandener outputStyle und eine bereits vorhandene
statusLine bleiben unveraendert (auch eine eigene des Projekts), ein bereits
vorhandener Hook-Befehl wird nicht ein zweites Mal angehaengt, und aendert sich
nichts, wird die Datei nicht angefasst.
Bei fehlender Datei oder kaputtem JSON: Meldung auf stderr, Exit-Code != 0,
Datei bleibt unangetastet.
"""

import copy
import json
import re
import sys


def lies_json(pfad, ersetzungen=None):
    """Liest eine JSON-Datei. Rueckgabe (daten, None) oder (None, fehlertext)."""
    try:
        with open(pfad, "r", encoding="utf-8") as f:
            roh = f.read()
    except FileNotFoundError:
        return None, "FEHLER: Settings-Datei nicht gefunden: %s" % pfad
    except OSError as fehler:
        return None, "FEHLER: %s nicht lesbar (%s)" % (pfad, fehler)

    if ersetzungen:
        for platzhalter, wert in ersetzungen.items():
            roh = roh.replace(platzhalter, wert)

    try:
        daten = json.loads(roh)
    except json.JSONDecodeError as fehler:
        return None, (
            "FEHLER: %s ist kein gueltiges JSON (%s) — Datei bleibt unveraendert."
            % (pfad, fehler)
        )

    if not isinstance(daten, dict):
        return None, (
            "FEHLER: %s enthaelt kein JSON-Objekt — Datei bleibt unveraendert."
            % pfad
        )
    return daten, None


def _befehle(eintrag):
    """Die Befehlszeilen eines Hook-Eintrags, als Menge vergleichbarer Strings."""
    return [
        json.dumps(h, sort_keys=True)
        for h in eintrag.get("hooks", [])
        if isinstance(h, dict)
    ]


_SKRIPT_RE = re.compile(r"([^/\"'\s]+/hooks/[^/\"'\s]+\.py)")


def _skript(hook):
    """Das Harness-Skript eines Hook-Befehls (z.B. `.claude/hooks/guard_tdd.py`)."""
    treffer = _SKRIPT_RE.search(str(hook.get("command", "")))
    return treffer.group(1) if treffer else None


def merge_hooks(ziel, quelle):
    """Fuegt die Hook-Eintraege aus `quelle` in `ziel` ein. Gibt True bei Aenderung.

    Gematcht wird pro Event ueber den `matcher` (fehlend zaehlt als eigener
    Fall). Bekannter Matcher -> nur die noch fehlenden Befehle anhaengen,
    unbekannter Matcher -> Eintrag komplett anhaengen. Fremde Eintraege bleiben
    dabei unberuehrt.
    """
    quell_hooks = quelle.get("hooks")
    if not isinstance(quell_hooks, dict):
        return False

    ziel_hooks = ziel.setdefault("hooks", {})
    if not isinstance(ziel_hooks, dict):
        raise ValueError('"hooks" ist kein JSON-Objekt')

    geaendert = False
    for event, eintraege in quell_hooks.items():
        if not isinstance(eintraege, list):
            continue
        bestand = ziel_hooks.setdefault(event, [])
        if not isinstance(bestand, list):
            raise ValueError('"hooks.%s" ist keine Liste' % event)

        for eintrag in eintraege:
            if not isinstance(eintrag, dict):
                continue
            matcher = eintrag.get("matcher")
            treffer = None
            for vorhanden in bestand:
                if isinstance(vorhanden, dict) and vorhanden.get("matcher") == matcher:
                    treffer = vorhanden
                    break

            if treffer is None:
                bestand.append(copy.deepcopy(eintrag))
                geaendert = True
                continue

            vorhandene_befehle = _befehle(treffer)
            for hook in eintrag.get("hooks", []):
                if not isinstance(hook, dict):
                    continue
                if json.dumps(hook, sort_keys=True) in vorhandene_befehle:
                    continue
                # Ein aelterer Befehl fuer dasselbe Waechter-Skript wird an seiner
                # Stelle ersetzt statt verdoppelt — sonst liefe jeder Waechter nach
                # einem Update zweimal.
                liste = treffer.setdefault("hooks", [])
                skript = _skript(hook)
                alt = next((i for i, h in enumerate(liste)
                            if skript and isinstance(h, dict) and _skript(h) == skript), None)
                if alt is None:
                    liste.append(copy.deepcopy(hook))
                else:
                    liste[alt] = copy.deepcopy(hook)
                geaendert = True

    return geaendert


def main(argv):
    if len(argv) not in (3, 5):
        sys.stderr.write(
            "Aufruf: python install_settings.py <settings.json> <style-name>"
            " [<hooks-quelle.json> <agentenordner>]\n"
        )
        return 2

    pfad, style = argv[1], argv[2]
    hooks_quelle = argv[3] if len(argv) == 5 else None
    agentenordner = argv[4] if len(argv) == 5 else None

    daten, fehler = lies_json(pfad)
    if fehler:
        sys.stderr.write(fehler + "\n")
        return 1

    geaendert = False

    if hooks_quelle:
        quelle, fehler = lies_json(
            hooks_quelle, {"<AGENTENORDNER>": agentenordner}
        )
        if fehler:
            sys.stderr.write(fehler + "\n")
            return 1
        try:
            if merge_hooks(daten, quelle):
                geaendert = True
        except ValueError as problem:
            sys.stderr.write(
                "FEHLER: %s in %s (%s) — Datei bleibt unveraendert.\n"
                % (problem, pfad, "Hook-Merge")
            )
            return 1
        print("  Hooks gemerged aus: %s" % hooks_quelle)

        if "statusLine" in quelle:
            if "statusLine" in daten:
                print("  Statuszeile bereits eingetragen, bleibt unveraendert")
            else:
                daten["statusLine"] = copy.deepcopy(quelle["statusLine"])
                geaendert = True
                print("  Statuszeile eingetragen")

    if "outputStyle" in daten:
        print("  Output-Style bereits eingetragen: %s" % daten["outputStyle"])
    else:
        daten["outputStyle"] = style
        geaendert = True
        print("  Output-Style eingetragen: %s" % style)

    if not geaendert:
        print("  Settings unveraendert (nichts nachzutragen)")
        return 0

    # newline="\n": gleiche Bytes unter Windows wie unter Linux/macOS —
    # Voraussetzung fuer den Paritaetstest zwischen install.sh und install.ps1.
    with open(pfad, "w", encoding="utf-8", newline="\n") as f:
        json.dump(daten, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
