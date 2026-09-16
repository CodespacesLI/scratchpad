#!/usr/bin/env python3
"""Installiert scratchpad in ein Zielprojekt — ein Installer fuer Windows, macOS und Linux.

    python install.py <pfad-zum-zielprojekt> [neutral|codex|claude]

Ohne Modus fragt der Installer nach. Er ersetzt die frueheren install.sh und
install.ps1: zwei Skripte mussten byte-gleich arbeiten, und jede Shell brachte eigene
Fallen mit (Bash 3.2 auf macOS, der Python-Platzhalter des Microsoft Store unter
Windows). Python ist ohnehin Voraussetzung, also gibt es genau einen Installer.

Nur Standardbibliothek, laeuft ab Python 3.9. Idempotent: ein zweiter Lauf ueberschreibt
die kopierten Dateien, haengt den AGENTS.md-Block nicht doppelt an und traegt keine
Hooks doppelt ein.
"""
from __future__ import annotations

import os
import shutil
import sys

import install_settings

QUELLE = os.path.dirname(os.path.abspath(__file__))
MODI = ("neutral", "codex", "claude")
PLATZHALTER = b"<AGENTENORDNER>"
PLATZHALTER_ENDUNGEN = (".md", ".json", ".py")
BLOCK_START = "<!-- scratchpad:start -->"
BLOCK_ENDE = "<!-- scratchpad:end -->"
STYLE = "scratchpad-projektleiter"


class InstallFehler(Exception):
    pass


class Installation:
    def __init__(self, ziel: str):
        self.ziel = ziel

    def _anzeige(self, pfad: str) -> str:
        return os.path.relpath(pfad, self.ziel).replace(os.sep, "/")

    def ordner(self, quelle: str, ziel: str) -> None:
        shutil.copytree(os.path.join(QUELLE, quelle), ziel, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        print("  kopiert: %s -> %s" % (quelle, self._anzeige(ziel)))

    def datei(self, quelle: str, ziel: str) -> None:
        os.makedirs(os.path.dirname(ziel), exist_ok=True)
        shutil.copyfile(os.path.join(QUELLE, quelle), ziel)
        print("  kopiert: %s -> %s" % (quelle, self._anzeige(ziel)))

    def hooks(self, ziel: str) -> None:
        os.makedirs(ziel, exist_ok=True)
        quelle = os.path.join(QUELLE, "hooks")
        for name in sorted(os.listdir(quelle)):
            if name.endswith(".py") and not name.startswith("test_"):
                shutil.copyfile(os.path.join(quelle, name), os.path.join(ziel, name))
        print("  kopiert: hooks -> %s" % self._anzeige(ziel))


def ersetze_platzhalter(basis: str, agentenordner: str) -> None:
    """Ersetzt <AGENTENORDNER> in allen Text-Dateien unter `basis`.

    Laeuft erst, wenn ALLES kopiert ist — sonst bleiben Platzhalter in Dateien stehen,
    die nach dem Ersetzen noch dazukommen (frueher: die Skills im Codex-Modus).
    Binaer gelesen und geschrieben, damit Zeilenenden und Kodierung unangetastet bleiben.
    """
    wert = agentenordner.encode("utf-8")
    for wurzel, _, dateien in os.walk(basis):
        for name in dateien:
            if not name.endswith(PLATZHALTER_ENDUNGEN):
                continue
            pfad = os.path.join(wurzel, name)
            with open(pfad, "rb") as fh:
                inhalt = fh.read()
            if PLATZHALTER in inhalt:
                with open(pfad, "wb") as fh:
                    fh.write(inhalt.replace(PLATZHALTER, wert))


def installiere_kern(inst: Installation, basis: str) -> None:
    inst.ordner("kern", os.path.join(basis, "vorgehen"))
    inst.datei("agent/AGENTS-block.md", os.path.join(basis, "INSTRUCTIONS.md"))
    inst.datei("uebung/referenzen.md", os.path.join(basis, "references", "referenzen.md"))


def ergaenze_agents_md(ziel: str, instructions: str) -> None:
    agents = os.path.join(ziel, "AGENTS.md")
    vorhanden = b""
    if os.path.exists(agents):
        with open(agents, "rb") as fh:
            vorhanden = fh.read()
    if BLOCK_START.encode() in vorhanden:
        print("  unveraendert: AGENTS.md (Scratchpad-Block bereits vorhanden)")
        return
    with open(instructions, "rb") as fh:
        block = fh.read()
    with open(agents, "ab") as fh:
        if os.path.exists(agents) and vorhanden:
            fh.write(b"\n")
        fh.write(BLOCK_START.encode() + b"\n" + block + b"\n" + BLOCK_ENDE.encode() + b"\n")
    print("  ergaenzt: AGENTS.md (Scratchpad-Block)")


def installiere(ziel: str, modus: str) -> None:
    os.makedirs(ziel, exist_ok=True)
    ziel = os.path.abspath(ziel)
    inst = Installation(ziel)
    print("Installiere Scratchpad (%s) nach: %s" % (modus, ziel))

    if modus in ("neutral", "codex"):
        basis = os.path.join(ziel, ".agents")
        installiere_kern(inst, basis)
        if modus == "codex":
            inst.ordner("agent/skills", os.path.join(basis, "skills"))
        ersetze_platzhalter(basis, ".agents")
        if modus == "codex":
            ergaenze_agents_md(ziel, os.path.join(basis, "INSTRUCTIONS.md"))
        return

    basis = os.path.join(ziel, ".claude")
    inst.ordner("kern", os.path.join(basis, "vorgehen"))
    inst.ordner("agent/commands", os.path.join(basis, "commands"))
    inst.ordner("agent/skills", os.path.join(basis, "skills"))
    inst.hooks(os.path.join(basis, "hooks"))
    inst.datei("kern/antwortform.md",
               os.path.join(basis, "output-styles", STYLE + ".md"))
    inst.datei("uebung/referenzen.md", os.path.join(basis, "references", "referenzen.md"))
    inst.datei("agent/statuszeile.js", os.path.join(basis, "statuszeile.js"))

    settings = os.path.join(basis, "settings.json")
    if not os.path.exists(settings):
        with open(settings, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("{}\n")
    rc = install_settings.main(["install_settings.py", settings, STYLE,
                                os.path.join(QUELLE, "agent", "settings-hooks.json"),
                                ".claude"])
    if rc != 0:
        raise InstallFehler("settings.json konnte nicht aktualisiert werden.")
    ersetze_platzhalter(basis, ".claude")


def frage_modus() -> str:
    try:
        return input("Zielmodus (neutral, codex, claude): ")
    except EOFError:
        return ""


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    aufruf = "Aufruf: python install.py <pfad-zum-zielprojekt> [neutral|codex|claude]"
    if not args or not args[0].strip():
        print("FEHLER: Pfad des Zielprojekts fehlt.\n" + aufruf, file=sys.stderr)
        return 1
    if len(args) > 2:
        print("FEHLER: Zu viele Argumente.\n" + aufruf, file=sys.stderr)
        return 1
    modus = (args[1] if len(args) == 2 else frage_modus()).strip().lower()
    if modus not in MODI:
        print("FEHLER: Unbekannter Zielmodus: %s (erlaubt: %s)" % (modus, ", ".join(MODI)),
              file=sys.stderr)
        return 1
    try:
        installiere(args[0], modus)
    except (InstallFehler, OSError) as fehler:
        print("FEHLER: %s" % fehler, file=sys.stderr)
        return 1
    print("Fertig. Scratchpad installiert (%s)." % modus)
    return 0


if __name__ == "__main__":
    sys.exit(main())
