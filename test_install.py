#!/usr/bin/env python3
"""Selbsttest fuer install.py und start.py — Aufruf: `python test_install.py`.

Reine asserts, kein Test-Framework (gleicher Runner-Stil wie test_treiber.py). Laeuft
unveraendert unter Windows, macOS, Linux und im Dev Container.

Abgedeckt: alle drei Modi, Idempotenz, bestehende AGENTS.md und settings.json bleiben
erhalten, kein <AGENTENORDNER> bleibt stehen, interaktive Modus-Auswahl, Fehlaufrufe,
Migration alter Hook-Befehle, der Hook-Befehl ueberspringt ein kaputtes `python3`
(Microsoft-Store-Platzhalter) und meldet fehlendes Python, start.py legt ein
Git-Projekt an, die Statuszeile wird im Claude-Modus eingerichtet (eine vorhandene
bleibt) und ihr Befehl laeuft unabhaengig vom aktuellen Ordner.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

HIER = os.path.dirname(os.path.abspath(__file__))
INSTALL = os.path.join(HIER, "install.py")
START = os.path.join(HIER, "start.py")
PLATZHALTER = b"<AGENTENORDNER>"

FEHLER = []


def check(name, bedingung, detail=""):
    status = "ok" if bedingung else "FEHLT"
    print("  [%s] %s%s" % (status, name, (" — " + detail) if detail and not bedingung else ""))
    if not bedingung:
        FEHLER.append(name)


def installiere(ziel, *args, eingabe=None):
    return subprocess.run([sys.executable, INSTALL, ziel, *args], input=eingabe,
                          capture_output=True, text=True)


def da(basis, rel):
    check("vorhanden: " + rel, os.path.isfile(os.path.join(basis, rel)))


def nicht_da(basis, rel):
    check("nicht vorhanden: " + rel, not os.path.exists(os.path.join(basis, rel)))


def lies(pfad):
    with open(pfad, encoding="utf-8") as fh:
        return fh.read()


def schreibe(pfad, inhalt):
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    with open(pfad, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(inhalt)


def mit_platzhalter(basis):
    treffer = []
    for wurzel, _, dateien in os.walk(basis):
        for name in dateien:
            pfad = os.path.join(wurzel, name)
            with open(pfad, "rb") as fh:
                if PLATZHALTER in fh.read():
                    treffer.append(os.path.relpath(pfad, basis))
    return treffer


def hook_befehle(settings_pfad):
    daten = json.loads(lies(settings_pfad))
    return [h["command"] for eintraege in daten.get("hooks", {}).values()
            for e in eintraege for h in e.get("hooks", [])]


def ok(proc, name):
    check(name, proc.returncode == 0, proc.stderr.strip()[-300:])


# ── Modi ──────────────────────────────────────────────────────────────────────
def test_neutral(wurzel):
    print("Modus neutral:")
    ziel = os.path.join(wurzel, "neutral")
    ok(installiere(ziel, "neutral"), "Installation laeuft")
    for rel in (".agents/vorgehen/01-brainstorm.md", ".agents/INSTRUCTIONS.md",
                ".agents/references/referenzen.md", ".agents/vorgehen/referenzen-holen.md"):
        da(ziel, rel)
    for rel in (".agents/skills", ".claude", "AGENTS.md", ".agents/statuszeile.js",
                ".agents/tasks/README.md"):
        nicht_da(ziel, rel)
    check("kein Platzhalter", not mit_platzhalter(ziel), str(mit_platzhalter(ziel)))
    check("Referenz-Einstieg in INSTRUCTIONS.md",
          "Referenzen:" in lies(os.path.join(ziel, ".agents/INSTRUCTIONS.md")))


def test_codex(wurzel):
    print("Modus codex (zweimal, bestehende AGENTS.md):")
    ziel = os.path.join(wurzel, "codex")
    schreibe(os.path.join(ziel, "AGENTS.md"), "# Eigene Regeln\n\nNicht ueberschreiben.\n")
    ok(installiere(ziel, "codex"), "erste Installation")
    ok(installiere(ziel, "CODEX"), "zweite Installation (Grossschreibung)")
    for rel in (".agents/vorgehen/03-build.md", ".agents/INSTRUCTIONS.md",
                ".agents/skills/grill-me/SKILL.md", ".agents/references/referenzen.md",
                ".agents/vorgehen/referenzen-holen.md"):
        da(ziel, rel)
    nicht_da(ziel, ".claude")
    nicht_da(ziel, ".agents/tasks/README.md")
    nicht_da(ziel, ".agents/statuszeile.js")
    check("kein Platzhalter (auch nicht in Skills)", not mit_platzhalter(ziel),
          str(mit_platzhalter(ziel)))
    agents = lies(os.path.join(ziel, "AGENTS.md"))
    check("bestehende AGENTS.md-Inhalte erhalten", "Nicht ueberschreiben." in agents)
    check("Referenz-Einstieg in AGENTS.md", "referenzen-holen.md" in agents)
    check("Scratchpad-Block genau einmal", agents.count("<!-- scratchpad:start -->") == 1)


def test_claude(wurzel):
    print("Modus claude (zweimal, bestehende settings.json):")
    ziel = os.path.join(wurzel, "claude")
    settings = os.path.join(ziel, ".claude", "settings.json")
    schreibe(settings, '{"permissions":{"allow":["Bash(ls:*)"]}}')
    ok(installiere(ziel, "claude"), "erste Installation")
    ok(installiere(ziel, "claude"), "zweite Installation")
    for rel in (".claude/vorgehen/01-brainstorm.md", ".claude/commands/build.md",
                ".claude/commands/ref.md", ".claude/skills/grill-me/SKILL.md",
                ".claude/hooks/guard_tdd.py", ".claude/hooks/hook_util.py",
                ".claude/output-styles/scratchpad-projektleiter.md",
                ".claude/references/referenzen.md", ".claude/vorgehen/referenzen-holen.md",
                ".claude/statuszeile.js"):
        da(ziel, rel)
    nicht_da(ziel, ".claude/tasks/README.md")
    nicht_da(ziel, ".claude/hooks/test_guard_tdd.py")
    nicht_da(ziel, ".claude/statuszeile.test.js")
    nicht_da(ziel, ".agents")
    check("kein Platzhalter", not mit_platzhalter(ziel), str(mit_platzhalter(ziel)))
    daten = json.loads(lies(settings))
    check("eigene permissions erhalten", daten.get("permissions", {}).get("allow") == ["Bash(ls:*)"])
    check("outputStyle gesetzt", daten.get("outputStyle") == "scratchpad-projektleiter")
    befehle = hook_befehle(settings)
    for waechter in ("guard_tdd.py", "guard_plan_drift.py", "guard_context_budget.py",
                     "guard_test_quality.py"):
        check("%s genau einmal eingetragen" % waechter,
              sum(waechter in b for b in befehle) == 1)
    statuszeile = daten.get("statusLine", {})
    check("statusLine eingetragen", statuszeile.get("type") == "command"
          and "/.claude/statuszeile.js" in statuszeile.get("command", ""), str(statuszeile))


def test_statuszeile_bleibt(wurzel):
    print("Eine eigene statusLine im Projekt wird nicht ueberschrieben:")
    ziel = os.path.join(wurzel, "eigene-statuszeile")
    settings = os.path.join(ziel, ".claude", "settings.json")
    eigene = {"type": "command", "command": "echo eigene-zeile"}
    schreibe(settings, json.dumps({"statusLine": eigene}))
    ok(installiere(ziel, "claude"), "Installation")
    check("eigene statusLine erhalten", json.loads(lies(settings)).get("statusLine") == eigene)


def test_hook_migration(wurzel):
    print("Alte Hook-Befehle (command -v python3 || ...) werden ersetzt, nicht verdoppelt:")
    ziel = os.path.join(wurzel, "migration")
    alt = ('"$(command -v python3 || command -v python)" '
           '"${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/%s"')
    schreibe(os.path.join(ziel, ".claude", "settings.json"), json.dumps({"hooks": {"Stop": [
        {"hooks": [{"type": "command", "command": alt % "guard_tdd.py"},
                   {"type": "command", "command": "echo eigener-hook"}]}]}}))
    ok(installiere(ziel, "claude"), "Installation")
    befehle = hook_befehle(os.path.join(ziel, ".claude", "settings.json"))
    tdd = [b for b in befehle if "guard_tdd.py" in b]
    check("guard_tdd.py genau einmal", len(tdd) == 1, str(tdd))
    check("neuer Befehl aktiv", bool(tdd) and "command -v" not in tdd[0])
    check("fremder Hook erhalten", "echo eigener-hook" in befehle)


def test_interaktiv_und_fehler(wurzel):
    print("Interaktive Auswahl und Fehlaufrufe:")
    ziel = os.path.join(wurzel, "interaktiv")
    ok(installiere(ziel, eingabe="neutral\n"), "Modus per Eingabe")
    da(ziel, ".agents/INSTRUCTIONS.md")
    check("ohne Pfad: Exit 1",
          subprocess.run([sys.executable, INSTALL], capture_output=True).returncode == 1)
    check("unbekannter Modus: Exit 1", installiere(ziel, "vim").returncode == 1)
    check("zu viele Argumente: Exit 1", installiere(ziel, "neutral", "x").returncode == 1)


# ── Hook-Befehl in einer echten Bash ──────────────────────────────────────────
def finde_bash():
    """Git Bash unter Windows (wie Claude Code sie nutzt), sonst die Bash im PATH.

    Unter Windows bewusst NICHT `shutil.which("bash")`: das findet oft
    System32\\bash.exe, den WSL-Starter, der ohne Distro nichts ausfuehrt.
    """
    if os.name != "nt":
        return shutil.which("bash")
    git = shutil.which("git")
    if not git:
        return None
    ordner = os.path.dirname(os.path.realpath(git))
    for _ in range(4):
        kandidat = os.path.join(ordner, "bin", "bash.exe")
        if os.path.isfile(kandidat):
            return kandidat
        ordner = os.path.dirname(ordner)
    return None


def test_hook_befehl(wurzel):
    print("Hook-Befehl: kaputtes python3 wird uebersprungen, fehlendes Python gemeldet:")
    bash = finde_bash()
    if not bash:
        print("  [--] uebersprungen: keine Bash gefunden")
        return
    ziel = os.path.join(wurzel, "hookbefehl")
    ok(installiere(ziel, "claude"), "Installation")
    settings = os.path.join(ziel, ".claude", "settings.json")
    befehl = next(b for b in hook_befehle(settings) if "guard_tdd.py" in b)
    befehl = befehl.replace("guard_tdd.py", "probe.py")
    schreibe(os.path.join(ziel, ".claude", "hooks", "probe.py"),
             "import os, sys\n"
             "ziel = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'probe.out')\n"
             "open(ziel, 'w').write(sys.stdin.read())\n")

    stubs = os.path.join(wurzel, "stubs")
    python = sys.executable.replace("\\", "/")
    schreibe(os.path.join(stubs, "python3"), "#!/bin/sh\nexit 49\n")
    schreibe(os.path.join(stubs, "python"), '#!/bin/sh\nexec "%s" "$@"\n' % python)
    for name in ("python3", "python"):
        os.chmod(os.path.join(stubs, name), 0o755)

    env = dict(os.environ, CLAUDE_PROJECT_DIR=ziel.replace("\\", "/"),
               PATH=stubs + os.pathsep + os.environ.get("PATH", ""))
    proc = subprocess.run([bash, "-c", befehl], input='{"probe": 1}', env=env,
                          capture_output=True, text=True, timeout=120)
    ok(proc, "Hook laeuft trotz kaputtem python3")
    out = os.path.join(ziel, ".claude", "hooks", "probe.out")
    check("Hook-Eingabe (stdin) kommt im Skript an",
          os.path.isfile(out) and lies(out) == '{"probe": 1}')

    leer = os.path.join(wurzel, "stubs-kaputt")
    for name in ("python3", "python"):
        schreibe(os.path.join(leer, name), "#!/bin/sh\nexit 49\n")
        os.chmod(os.path.join(leer, name), 0o755)
    env["PATH"] = leer
    proc = subprocess.run([bash, "-c", befehl], input="{}", env=env,
                          capture_output=True, text=True, timeout=120)
    check("ohne Python: Exit 1 mit Meldung",
          proc.returncode == 1 and "kein lauffaehiges Python" in proc.stderr,
          "rc=%s stderr=%s" % (proc.returncode, proc.stderr.strip()))


def test_statuszeile_befehl(wurzel):
    print("Statuszeilen-Befehl laeuft in Bash mit Node, auch aus einem anderen Ordner:")
    bash, node = finde_bash(), shutil.which("node")
    if not bash or not node:
        print("  [--] uebersprungen: Bash oder Node fehlt")
        return
    ziel = os.path.join(wurzel, "statuszeile")
    ok(installiere(ziel, "claude"), "Installation")
    befehl = json.loads(lies(os.path.join(ziel, ".claude", "settings.json")))["statusLine"]["command"]
    anderswo = os.path.join(wurzel, "anderswo")
    os.makedirs(anderswo, exist_ok=True)
    env = dict(os.environ, CLAUDE_PROJECT_DIR=ziel.replace("\\", "/"))
    proc = subprocess.run([bash, "-c", befehl], cwd=anderswo, env=env, capture_output=True,
                          text=True, timeout=120,
                          input=json.dumps({"model": {"display_name": "Testmodell"},
                                            "cost": {"total_cost_usd": 0.5}}))
    ok(proc, "Befehl laeuft")
    check("Zeile nennt Modell und Kosten",
          "Testmodell" in proc.stdout and "$0.5000" in proc.stdout, proc.stdout)


# ── start.py ──────────────────────────────────────────────────────────────────
def test_start(wurzel):
    print("start.py legt das Uebungsprojekt als Git-Projekt an:")
    ziel = os.path.join(wurzel, "start", "task-board")
    proc = subprocess.run([sys.executable, START, "codex", ziel], capture_output=True, text=True)
    ok(proc, "start.py laeuft")
    da(ziel, "AGENTS.md")
    if shutil.which("git"):
        check("Git-Projekt angelegt", os.path.isdir(os.path.join(ziel, ".git")))
    check("nennt den naechsten Befehl", "  codex" in proc.stdout.splitlines(), proc.stdout)


def main():
    wurzel = tempfile.mkdtemp(prefix="scratchpad-test-")
    try:
        for test in (test_neutral, test_codex, test_claude, test_statuszeile_bleibt,
                     test_hook_migration, test_interaktiv_und_fehler, test_hook_befehl,
                     test_statuszeile_befehl, test_start):
            test(wurzel)
    finally:
        shutil.rmtree(wurzel, ignore_errors=True)
    if FEHLER:
        print("\nFEHLGESCHLAGEN: %d Pruefung(en): %s" % (len(FEHLER), ", ".join(FEHLER)))
        return 1
    print("\nAlle Installer-Pruefungen bestanden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
