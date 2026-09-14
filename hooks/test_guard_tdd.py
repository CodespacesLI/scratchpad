#!/usr/bin/env python3
"""Selbsttest fuer guard_tdd.py — Aufruf: `python test_guard_tdd.py`.

Reine asserts, kein Test-Framework. Der Wächter arbeitet auf dem Change-Set eines
Arbeitsverzeichnisses; die Tests legen dafür je ein Wegwerf-Repo im Temp-Verzeichnis an
(nie im echten Projekt). Deckt ab: Kernfall (Logik ohne Test blockt), Normalbetrieb
(Logik mit passendem Test bleibt still), Fingerprint-Dedupe und die fail-open-Pfade.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HOOKS_DIR, "guard_tdd.py")

sys.path.insert(0, HOOKS_DIR)
import guard_tdd  # noqa: E402  (erst nach dem sys.path-Eintrag importierbar)

# Aus dem Wächter gelesen, nicht abgeschrieben: der Installer ersetzt den
# Agenten-Ordner beim Kopieren, der Test muss trotzdem stimmen.
FP_REL = guard_tdd.FP_DEFAULT


def make_repo(tmp: str) -> str:
    """Wegwerf-Repo im Temp-Verzeichnis (nur dort wird git angefasst)."""
    repo = os.path.join(tmp, "repo")
    os.makedirs(repo, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=repo, capture_output=True,
                   text=True, timeout=15)
    return repo


def add_file(repo: str, rel: str, content: str = "x = 1\n") -> None:
    path = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def run_hook(repo: str, raw_stdin=None, **payload_extra):
    payload = {"stop_hook_active": False, "session_id": "s"}
    payload.update(payload_extra)
    data = raw_stdin if raw_stdin is not None else json.dumps(payload)
    return subprocess.run([sys.executable, HOOK], input=data, capture_output=True,
                          text=True, timeout=20, cwd=repo)


def test_logic_without_test_blocks(tmp):
    repo = make_repo(tmp)
    add_file(repo, "src/service.py", "def compute():\n    return 42\n")
    proc = run_hook(repo)
    assert proc.returncode == 2, f"Logik ohne Test muss blocken, war {proc.returncode}"
    assert "src/service.py" in proc.stderr, proc.stderr


def test_logic_with_matching_test_passes(tmp):
    repo = make_repo(tmp)
    add_file(repo, "src/service.py", "def compute():\n    return 42\n")
    add_file(repo, "src/test_service.py", "def test_compute():\n    assert compute() == 42\n")
    proc = run_hook(repo)
    assert proc.returncode == 0, f"Logik mit Test muss still bleiben: {proc.stderr}"


def test_unrelated_test_does_not_cover(tmp):
    """Ein Test irgendwo im Change-Set deckt nicht jede beliebige Logik-Datei."""
    repo = make_repo(tmp)
    add_file(repo, "backend/billing/rechnung.py", "def summe():\n    return 1\n")
    add_file(repo, "frontend/ui/knopf.test.ts", "it('x', () => { expect(1).toBe(1) })\n")
    proc = run_hook(repo)
    assert proc.returncode == 2, "unverwandter Test darf die Logik nicht decken"
    assert "rechnung.py" in proc.stderr, proc.stderr


def test_exempt_paths_stay_silent(tmp):
    repo = make_repo(tmp)
    add_file(repo, "db/migrations/001_init.py", "SQL = 'x'\n")
    add_file(repo, "vite.config.ts", "export default {}\n")
    add_file(repo, "docs/anleitung.md", "# Text\n")
    proc = run_hook(repo)
    assert proc.returncode == 0, f"Migration/Config/Doku sind keine Logik: {proc.stderr}"


def test_fingerprint_dedupe_silences_second_turn(tmp):
    repo = make_repo(tmp)
    add_file(repo, "src/service.py", "def compute():\n    return 42\n")
    first = run_hook(repo)
    assert first.returncode == 2, "erster Lauf muss warnen"
    assert os.path.isfile(os.path.join(repo, FP_REL)), \
        f"Fingerprint gehört nach {FP_REL}"
    second = run_hook(repo)
    assert second.returncode == 0, "unveränderte Liste darf nicht erneut nerven"


def test_changed_uncovered_list_warns_again(tmp):
    repo = make_repo(tmp)
    add_file(repo, "src/service.py", "def compute():\n    return 42\n")
    assert run_hook(repo).returncode == 2
    add_file(repo, "src/andere.py", "def x():\n    return 1\n")
    proc = run_hook(repo)
    assert proc.returncode == 2, "neue ungedeckte Datei muss wieder warnen"


def test_loop_guard_and_subagent_stay_silent(tmp):
    repo = make_repo(tmp)
    add_file(repo, "src/service.py", "def compute():\n    return 42\n")
    assert run_hook(repo, stop_hook_active=True).returncode == 0, "Loop-Schutz fehlt"
    assert run_hook(repo, agent_id="a1").returncode == 0, "Subagent-Stop muss still sein"


def test_broken_stdin_fails_open(tmp):
    repo = make_repo(tmp)
    add_file(repo, "src/service.py", "def compute():\n    return 42\n")
    proc = run_hook(repo, raw_stdin="{kein json")
    assert proc.returncode == 0, f"kaputtes stdin muss fail-open sein: {proc.returncode}"
    assert "Traceback" not in proc.stderr, proc.stderr


TESTS = [
    test_logic_without_test_blocks,
    test_logic_with_matching_test_passes,
    test_unrelated_test_does_not_cover,
    test_exempt_paths_stay_silent,
    test_fingerprint_dedupe_silences_second_turn,
    test_changed_uncovered_list_warns_again,
    test_loop_guard_and_subagent_stay_silent,
    test_broken_stdin_fails_open,
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
