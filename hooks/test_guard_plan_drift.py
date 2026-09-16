#!/usr/bin/env python3
"""Selbsttest fuer guard_plan_drift.py — Aufruf: `python test_guard_plan_drift.py`.

Reine asserts, kein Test-Framework (gleicher Runner wie die uebrigen Wächter-Tests).
Der Wächter vergleicht den Plan-Stand über das Change-Set-Fenster; die Tests legen dafür
je ein Wegwerf-Repo im Temp-Verzeichnis an (nie im echten Projekt).

Geprueft wird die VERENGTE Semantik: gemeldet wird ausschliesslich die unbegründet
verschwundene Task-Zeile. Abhaken, Umformulieren, begründetes Streichen, Arbeiten ohne
Plan-Berührung und fehlende Formalia sind ausdrücklich still — genau daran krankte die
alte Fassung (Fehlalarm in fast jedem Turn).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HOOKS_DIR, "guard_plan_drift.py")

sys.path.insert(0, HOOKS_DIR)
import guard_plan_drift  # noqa: E402  (erst nach dem sys.path-Eintrag importierbar)

TASKS_DIR = guard_plan_drift.DEFAULT_TASKS_DIR

PLAN_IM_BAU = """# Bauplan Anmeldung

Status: im-bau

- [ ] Task 1 — Formular bauen
- [ ] Task 2 — Fehlermeldung anzeigen
- [ ] Task 3 — Sitzung ablaufen lassen
"""


def git(repo: str, *args: str):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True,
                          timeout=20)


def make_repo(tmp: str, plan: str = PLAN_IM_BAU) -> str:
    """Wegwerf-Repo mit committetem Bauplan (nur im Temp-Verzeichnis wird git angefasst)."""
    repo = os.path.join(tmp, "repo")
    os.makedirs(repo, exist_ok=True)
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "config", "user.name", "Test")
    write(repo, os.path.join(TASKS_DIR, "anmeldung.md"), plan)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "plan")
    return repo


def write(repo: str, rel: str, content: str) -> None:
    path = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def plan_ersetzen(repo: str, content: str, name: str = "anmeldung.md") -> None:
    write(repo, os.path.join(TASKS_DIR, name), content)


def run_hook(repo: str, raw_stdin=None, **payload_extra):
    payload = {"stop_hook_active": False, "session_id": "s1"}
    payload.update(payload_extra)
    data = raw_stdin if raw_stdin is not None else json.dumps(payload)
    # Feste UTF-8-Dekodierung: die Meldung trägt Umlaute und Gedankenstriche, die unter
    # der Landes-Codepage sonst als Zeichensalat oder gar nicht ankämen.
    return subprocess.run([sys.executable, HOOK], input=data, capture_output=True,
                          encoding="utf-8", errors="replace", timeout=25, cwd=repo)


def test_verschwundene_taskzeile_warnt(tmp):
    repo = make_repo(tmp)
    plan_ersetzen(repo, PLAN_IM_BAU.replace(
        "- [ ] Task 2 — Fehlermeldung anzeigen\n", ""))
    proc = run_hook(repo)
    assert proc.returncode == 2, f"stille Kürzung muss melden, war {proc.returncode}"
    assert "Fehlermeldung" in proc.stderr, proc.stderr


def test_abhaken_bleibt_still(tmp):
    repo = make_repo(tmp)
    plan_ersetzen(repo, PLAN_IM_BAU.replace(
        "- [ ] Task 2 — Fehlermeldung anzeigen",
        "- [x] Task 2 — Fehlermeldung anzeigen"))
    proc = run_hook(repo)
    assert proc.returncode == 0, f"Abhaken ist keine Kürzung: {proc.stderr}"


def test_umformulierung_bleibt_still(tmp):
    repo = make_repo(tmp)
    plan_ersetzen(repo, PLAN_IM_BAU.replace(
        "- [ ] Task 2 — Fehlermeldung anzeigen",
        "- [ ] **Task 2** Fehlermeldung anzeigen (deutsch)"))
    proc = run_hook(repo)
    assert proc.returncode == 0, f"Umformulieren ist keine Kürzung: {proc.stderr}"


def test_begruendete_streichung_bleibt_still(tmp):
    repo = make_repo(tmp)
    plan_ersetzen(repo, PLAN_IM_BAU.replace(
        "- [ ] Task 2 — Fehlermeldung anzeigen\n",
        "Task 2 gestrichen: die Fehlermeldung kommt aus dem Formular selbst.\n"))
    proc = run_hook(repo)
    assert proc.returncode == 0, f"begründete Streichung ist der erlaubte Weg: {proc.stderr}"


def test_entwurf_wird_nicht_geprueft(tmp):
    """Solange der Plan Entwurf ist, kommen und gehen Zeilen legitim."""
    entwurf = PLAN_IM_BAU.replace("Status: im-bau", "Status: entwurf")
    repo = make_repo(tmp, entwurf)
    plan_ersetzen(repo, entwurf.replace("- [ ] Task 2 — Fehlermeldung anzeigen\n", ""))
    proc = run_hook(repo)
    assert proc.returncode == 0, f"Entwurf ist noch nicht abgesprochen: {proc.stderr}"


def test_fertiger_plan_wird_geprueft(tmp):
    fertig = PLAN_IM_BAU.replace("Status: im-bau", "Status: fertig")
    repo = make_repo(tmp, fertig)
    plan_ersetzen(repo, fertig.replace("- [ ] Task 2 — Fehlermeldung anzeigen\n", ""))
    proc = run_hook(repo)
    assert proc.returncode == 2, "auch aus einem fertigen Plan verschwindet nichts still"


def test_code_ohne_plan_beruehrung_bleibt_still(tmp):
    """Der Fehlalarm der alten Fassung: gebaut, Plan nicht angefasst, offene Punkte da."""
    repo = make_repo(tmp)
    write(repo, "src/anmeldung.py", "def anmelden():\n    return True\n")
    proc = run_hook(repo)
    assert proc.returncode == 0, f"Weiterarbeiten am Stück ist der Normalfall: {proc.stderr}"


def test_fehlende_formalia_bleiben_still(tmp):
    """Fehlende Akzeptanzkriterien/Checkboxen sind Formfragen, keine Kürzung."""
    repo = make_repo(tmp, "# Bauplan\n\nStatus: im-bau\n\n- [ ] Task 1 — irgendwas\n")
    plan_ersetzen(repo, "# Bauplan\n\nStatus: im-bau\n\n- [ ] Task 1 — irgendwas\n"
                        "- [ ] Task 2 — noch etwas\n")
    proc = run_hook(repo)
    assert proc.returncode == 0, f"Hinzufügen ohne Kriterien ist kein Drift: {proc.stderr}"


def test_geloeschte_plandatei_bleibt_still(tmp):
    """Eine ganz verschwundene Plan-Datei (Archivierung) ist nie ein Signal."""
    repo = make_repo(tmp)
    os.remove(os.path.join(repo, TASKS_DIR, "anmeldung.md"))
    proc = run_hook(repo)
    assert proc.returncode == 0, f"archivierter Plan ist kein Drift: {proc.stderr}"


def test_readme_ist_kein_plan(tmp):
    repo = make_repo(tmp)
    write(repo, os.path.join(TASKS_DIR, "README.md"),
          "Status: im-bau\n- [ ] Beispielzeile aus der Doku\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "readme")
    write(repo, os.path.join(TASKS_DIR, "README.md"), "Status: im-bau\n")
    proc = run_hook(repo)
    assert proc.returncode == 0, f"README ist Konventions-Doku, kein Plan: {proc.stderr}"


def test_loop_schutz_und_subagent_still(tmp):
    repo = make_repo(tmp)
    plan_ersetzen(repo, PLAN_IM_BAU.replace(
        "- [ ] Task 2 — Fehlermeldung anzeigen\n", ""))
    assert run_hook(repo, stop_hook_active=True).returncode == 0, "Loop-Schutz fehlt"
    assert run_hook(repo, agent_id="a1").returncode == 0, "Subagent-Stop muss still sein"


def test_kaputtes_stdin_faellt_offen(tmp):
    repo = make_repo(tmp)
    plan_ersetzen(repo, PLAN_IM_BAU.replace(
        "- [ ] Task 2 — Fehlermeldung anzeigen\n", ""))
    proc = run_hook(repo, raw_stdin="{kein json")
    assert proc.returncode == 0, f"kaputtes stdin muss fail-open sein: {proc.returncode}"
    assert "Traceback" not in proc.stderr, proc.stderr


def test_ohne_repo_still(tmp):
    """Ohne git gibt es kein Vorher/Nachher — dann wird nicht geraten."""
    kein_repo = os.path.join(tmp, "leer")
    os.makedirs(os.path.join(kein_repo, TASKS_DIR), exist_ok=True)
    write(kein_repo, os.path.join(TASKS_DIR, "plan.md"), PLAN_IM_BAU)
    proc = run_hook(kein_repo)
    assert proc.returncode == 0, f"kein Repo -> still: {proc.stderr}"


def test_plan_unter_punkt_claude_tasks_wird_geprueft(tmp):
    """Baupläne liegen unter `.claude/tasks/<slug>.md` — dort muss der Wächter suchen.

    Der Ort der Ablage ist keine Kosmetik: sucht der Wächter am alten Ort, bleibt jede
    stille Kürzung eines echten Bauplans unbemerkt — er ist dann nur noch Dekoration.
    Der Pfad steht hier bewusst WÖRTLICH, nicht über die Konstante des Wächters: der
    Test soll die Ablage festnageln, nicht dem Wächter hinterherlaufen.
    """
    repo = os.path.join(tmp, "repo")
    os.makedirs(repo, exist_ok=True)
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "config", "user.name", "Test")
    write(repo, ".claude/tasks/anmeldung.md", PLAN_IM_BAU)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "plan")
    write(repo, ".claude/tasks/anmeldung.md",
          PLAN_IM_BAU.replace("- [ ] Task 2 — Fehlermeldung anzeigen\n", ""))
    proc = run_hook(repo)
    assert proc.returncode == 2,         f"Plan unter .claude/tasks muss geprüft werden, war {proc.returncode}"
    assert "Fehlermeldung" in proc.stderr, proc.stderr


def test_archiv_unter_punkt_claude_tasks_done_bleibt_still(tmp):
    """Fertige Pläne liegen unter `.claude/tasks/done/` — der Glob steigt da nicht hinein."""
    repo = os.path.join(tmp, "repo")
    os.makedirs(repo, exist_ok=True)
    git(repo, "init", "-q")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "config", "user.name", "Test")
    write(repo, ".claude/tasks/done/anmeldung.md", PLAN_IM_BAU)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "plan")
    write(repo, ".claude/tasks/done/anmeldung.md",
          PLAN_IM_BAU.replace("- [ ] Task 2 — Fehlermeldung anzeigen\n", ""))
    proc = run_hook(repo)
    assert proc.returncode == 0, f"das Archiv ist abgeschlossen: {proc.stderr}"


def test_meldung_ist_utf8_auch_unter_fremder_codepage(tmp):
    """Umlaute kommen als gültiges UTF-8 an — mit und ohne hook_util daneben.

    Nachgestellt wird Windows: stderr läuft dort ohne Zutun in der Landes-Codepage
    (cp1252), Claude Code liest aber UTF-8. Erzwungen per Variable, damit der Fall auf
    jedem Betriebssystem reproduzierbar ist.
    """
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "cp1252"
    env["PYTHONUTF8"] = "0"
    allein = os.path.join(tmp, "allein")
    os.makedirs(allein)
    kopie = os.path.join(allein, "guard_plan_drift.py")
    shutil.copyfile(HOOK, kopie)
    repo = make_repo(tmp)
    plan_ersetzen(repo, PLAN_IM_BAU.replace(
        "- [ ] Task 2 — Fehlermeldung anzeigen\n", ""))
    for hook in (HOOK, kopie):
        proc = subprocess.run([sys.executable, hook], input=b'{"session_id": "s1"}',
                              capture_output=True, timeout=25, cwd=repo, env=env)
        assert proc.returncode == 2, f"muss melden ({hook}): {proc.stderr!r}"
        try:
            text = proc.stderr.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise AssertionError(f"stderr ist kein UTF-8 ({hook}): {exc}; "
                                 f"{proc.stderr[:60]!r}")
        assert "begründet" in text and "Task 2 — Fehlermeldung" in text, text


TESTS = [
    test_verschwundene_taskzeile_warnt,
    test_abhaken_bleibt_still,
    test_umformulierung_bleibt_still,
    test_begruendete_streichung_bleibt_still,
    test_entwurf_wird_nicht_geprueft,
    test_fertiger_plan_wird_geprueft,
    test_code_ohne_plan_beruehrung_bleibt_still,
    test_fehlende_formalia_bleiben_still,
    test_geloeschte_plandatei_bleibt_still,
    test_readme_ist_kein_plan,
    test_plan_unter_punkt_claude_tasks_wird_geprueft,
    test_archiv_unter_punkt_claude_tasks_done_bleibt_still,
    test_loop_schutz_und_subagent_still,
    test_kaputtes_stdin_faellt_offen,
    test_ohne_repo_still,
    test_meldung_ist_utf8_auch_unter_fremder_codepage,
]


def main() -> int:
    failures = []
    for test in TESTS:
        try:
            with tempfile.TemporaryDirectory() as tmp:
                test(tmp)
        except Exception as exc:
            failures.append(f"FAIL {test.__name__}: {exc}")
        else:
            print(f"ok   {test.__name__}")
    for line in failures:
        print(line, file=sys.stderr)
    print(f"\n{len(TESTS) - len(failures)}/{len(TESTS)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
