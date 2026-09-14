#!/usr/bin/env python3
"""Selbsttest fuer guard_test_quality.py — Aufruf: `python test_guard_test_quality.py`.

Reine asserts, kein Test-Framework. Deckt die vier Befunde ab (Test ohne Assertion,
tautologische Assertion, Secret-artiges Literal, Skip ohne Begründung), den
Normalbetrieb (sauberer Test bleibt still) und die fail-open-Pfade.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HOOKS_DIR, "guard_test_quality.py")


def run_hook(path, content, tool_name="Write", raw_stdin=None):
    payload = json.dumps({
        "tool_name": tool_name,
        "session_id": "s",
        "tool_input": {"file_path": path, "content": content},
    })
    return subprocess.run([sys.executable, HOOK],
                          input=raw_stdin if raw_stdin is not None else payload,
                          capture_output=True, text=True, timeout=15)


def test_test_without_assertion_warns():
    proc = run_hook("src/rechnung.test.ts",
                    "it('rechnet', () => {\n  const summe = rechne(2, 3)\n})\n")
    assert proc.returncode == 2, f"Test ohne Assertion muss warnen, war {proc.returncode}"
    assert "Assertion" in proc.stderr, proc.stderr


def test_clean_test_stays_silent():
    proc = run_hook("src/rechnung.test.ts",
                    "it('rechnet', () => {\n  expect(rechne(2, 3)).toBe(5)\n})\n")
    assert proc.returncode == 0, f"sauberer Test muss still bleiben: {proc.stderr}"


def test_tautological_assertion_warns():
    proc = run_hook("src/rechnung.test.ts",
                    "it('rechnet', () => {\n  expect(true).toBe(true)\n})\n")
    assert proc.returncode == 2, "tautologische Assertion muss warnen"
    assert "Tautolog" in proc.stderr, proc.stderr


def test_secret_like_literal_warns():
    content = ("it('meldet an', () => {\n"
               "  const token = 'a3f9c1d2e4b6a8c0f2e4d6b8a0c2e4f6'\n"
               "  expect(login(token)).toBe(true)\n})\n")
    proc = run_hook("src/login.test.ts", content)
    assert proc.returncode == 2, "Secret-artiges Literal muss warnen"
    assert "Secret" in proc.stderr, proc.stderr


def test_skip_without_reason_warns_but_with_reason_is_silent():
    ohne = "it.skip('rechnet', () => {\n  expect(rechne(2, 3)).toBe(5)\n})\n"
    proc = run_hook("src/rechnung.test.ts", ohne)
    assert proc.returncode == 2, "Skip ohne Begründung muss warnen"
    mit = ("// wartet auf Task 4 (neue API)\n" + ohne)
    proc = run_hook("src/rechnung.test.ts", mit)
    assert proc.returncode == 0, f"Skip mit Begründung ist in Ordnung: {proc.stderr}"


def test_java_disabled_without_reason_warns():
    content = ("class RechnungTest {\n  @Disabled\n  @Test\n"
               "  void rechnet() { assertThat(rechne(2, 3)).isEqualTo(5); }\n}\n")
    proc = run_hook("backend/src/test/java/RechnungTest.java", content)
    assert proc.returncode == 2, "@Disabled ohne Begründung muss warnen"


def test_non_test_file_is_ignored():
    proc = run_hook("src/rechnung.ts", "export const rechne = (a, b) => a + b\n")
    assert proc.returncode == 0, f"Produktivcode ist nicht Gegenstand: {proc.stderr}"


def test_helper_file_without_test_bodies_is_ignored():
    proc = run_hook("src/fixtures.test.ts", "export const kunde = { name: 'Ada' }\n")
    assert proc.returncode == 0, f"Datei ohne Test-Rümpfe: {proc.stderr}"


def test_broken_stdin_and_other_tools_fail_open():
    proc = run_hook(None, None, raw_stdin="{kein json")
    assert proc.returncode == 0, proc.stderr
    assert "Traceback" not in proc.stderr, proc.stderr
    proc = run_hook("src/rechnung.test.ts", "it('x', () => {})\n", tool_name="Read")
    assert proc.returncode == 0, "anderes Tool ist nicht Gegenstand"


TESTS = [
    test_test_without_assertion_warns,
    test_clean_test_stays_silent,
    test_tautological_assertion_warns,
    test_secret_like_literal_warns,
    test_skip_without_reason_warns_but_with_reason_is_silent,
    test_java_disabled_without_reason_warns,
    test_non_test_file_is_ignored,
    test_helper_file_without_test_bodies_is_ignored,
    test_broken_stdin_and_other_tools_fail_open,
]


def main() -> int:
    failures = []
    for test in TESTS:
        try:
            test()
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
