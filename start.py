#!/usr/bin/env python3
"""Legt das Uebungsprojekt an — der eine Befehl nach dem Setup.

    python start.py [claude|codex] [pfad]

Ohne Pfad entsteht das Projekt im Ordner `task-board/` neben dieser Datei (per
.gitignore aus dem scratchpad-Repo ausgeschlossen). Das funktioniert gleich auf dem
eigenen Rechner, im Dev Container und in Codespaces. Der Schritt installiert den
gewaehlten Modus, macht den Ordner zum Git-Projekt und nennt die naechsten Befehle.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

import install

HIER = os.path.dirname(os.path.abspath(__file__))
STANDARD_ZIEL = os.path.join(HIER, "task-board")
AGENTEN = ("claude", "codex")


def warne_fehlende(modus: str) -> None:
    noetig = ["git", "node", "npm"] + ([modus] if modus in AGENTEN else [])
    fehlt = [name for name in noetig if shutil.which(name) is None]
    if fehlt:
        print("WARNUNG: nicht gefunden: %s. Erst das Setup ausfuehren (siehe README)."
              % ", ".join(fehlt), file=sys.stderr)


def git_init(ziel: str) -> None:
    if os.path.exists(os.path.join(ziel, ".git")):
        print("  unveraendert: Git-Projekt besteht bereits")
        return
    if shutil.which("git") is None:
        print("WARNUNG: git fehlt, Projekt nicht als Git-Projekt angelegt.", file=sys.stderr)
        return
    subprocess.run(["git", "init", "-q"], cwd=ziel, check=True)
    print("  angelegt: Git-Projekt")


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) > 2:
        print("Aufruf: python start.py [claude|codex] [pfad]", file=sys.stderr)
        return 1
    modus = (args[0] if args else install.frage_modus()).strip().lower()
    ziel = os.path.abspath(args[1] if len(args) == 2 else STANDARD_ZIEL)

    if modus in install.MODI:
        warne_fehlende(modus)
    rc = install.main([ziel, modus])
    if rc != 0:
        return rc
    git_init(ziel)

    print()
    print("Weiter im Terminal:")
    print("  cd %s" % os.path.relpath(ziel))
    if modus in AGENTEN:
        print("  %s" % modus)
    arbeitsblatt = "aufgabe-%s.md" % modus if modus in AGENTEN else "aufgabe.md"
    print("Arbeitsblatt: %s" % os.path.join("uebung", arbeitsblatt))
    return 0


if __name__ == "__main__":
    sys.exit(main())
