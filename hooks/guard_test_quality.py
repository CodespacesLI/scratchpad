#!/usr/bin/env python3
"""PostToolUse-Wächter: billige, deterministische Prüfung der Test-QUALITÄT.

Hintergrund: Testcode gehört nicht durch ein teures Review geschleust — die typischen
Test-Fehlerbilder sind deterministisch fangbar, und genau die fängt dieser Wächter direkt
beim Schreiben ab.

Bei einem Treffer: exit 2 plus Meldung auf stderr, der Bearbeiter korrigiert sofort.
Wenig Fehlalarm und fail-open (jeder Eigenfehler endet still). Greift nur auf Testdateien.

SPRACH-ABDECKUNG (bewusst begrenzt, erweiterbar):
  * "ts"   — JS/TS-Ökosystem: *.test.ts|tsx|js|jsx, *.spec.ts|tsx
  * "java" — JVM-Ökosystem: *.java unterhalb eines `/src/test/`-Pfads
Andere Sprachen prüft dieser Wächter bewusst NICHT — für die greift nur der generische
TDD-Boden (`guard_tdd.py`, reine Test-Anwesenheit). Eine neue Sprache abdecken heisst:
einen Eintrag in `is_test_file` plus passende Muster für Assertion, Tautologie und Skip.

Gefundene Fehlerbilder je abgedeckter Sprache:
  - Testdatei ohne jede Assertion — ein Test, der nichts prüft
  - tautologische Assertion (`expect(true).toBe(true)`, `assertTrue(true)`)
  - Secret-artige Literale in Fixtures (lange Hex- oder Base64-Ketten)
  - `test.skip` / `it.skip` / `xtest` / `@Disabled` ohne Begründungs-Kommentar
"""
from __future__ import annotations

import json
import os
import re
import sys

try:
    from hook_util import use_utf8_stdio
except Exception:  # Helfer fehlt -> dieselbe Umstellung lokal, die Meldung muss lesbar bleiben
    def use_utf8_stdio():
        for stream in (sys.stdin, sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

# --- Welche Dateien sind Tests? ----------------------------------------------
TS_TEST = (".test.ts", ".test.tsx", ".test.js", ".test.jsx",
           ".spec.ts", ".spec.tsx")
JAVA_TEST_MARKER = "/src/test/"


def is_test_file(path):
    norm = path.replace(os.sep, "/")
    if norm.endswith(TS_TEST):
        return True, "ts"
    if norm.endswith(".java") and JAVA_TEST_MARKER in norm:
        return True, "java"
    return False, ""


# --- Muster ------------------------------------------------------------------
TS_ASSERT = re.compile(r"\b(?:expect|assert)\s*\(")
JAVA_ASSERT = re.compile(r"\b(?:assert\w*|verify|assertThat|then\w*|expect)\s*\(")
TS_TAUTOLOGY = re.compile(
    r"expect\s*\(\s*(true|false|1|0)\s*\)\s*\.\s*toBe\s*\(\s*\1\s*\)"
)
JAVA_TAUTOLOGY = re.compile(
    r"\bassert(?:True\s*\(\s*true|False\s*\(\s*false|Equals\s*\(\s*([^,]+?)\s*,\s*\1\s*\))"
)
# Secret-artig: mindestens 32 Zeichen Hex, oder lange Base64-ähnliche Ketten.
SECRET_LIKE = re.compile(
    r"['\"][0-9a-fA-F]{32,}['\"]"
    r"|['\"][A-Za-z0-9+/]{40,}={0,2}['\"]"
)
# Erlaubt: offensichtliche Test-Fixtures (Null-UUIDs, „test"/„beispiel"-Ketten).
SECRET_ALLOW = re.compile(
    r"0{8}-0{4}|deadbeef|example|beispiel|test[_-]?(token|key|secret)|xxx+",
    re.IGNORECASE,
)
TS_SKIP = re.compile(r"\b(?:test|it|describe)\.skip\s*\(|\bx(?:test|it|describe)\s*\(")
JAVA_SKIP = re.compile(r"@Disabled\b")

# Trägt die Datei überhaupt Test-Rümpfe? (Reine Helfer-/Fixture-Dateien sind kein Thema.)
# Modifizierer wie `.skip` / `.each` / `.only` zählen mit: sonst wäre ausgerechnet eine
# Datei aus lauter übersprungenen Tests von der Prüfung ausgenommen.
HAS_TEST_BODY = re.compile(
    r"\b(?:test|it|describe)\s*(?:\.\w+\s*)?\(|\bx(?:test|it|describe)\s*\(|@Test\b|@Disabled\b"
)


def extract(tool_input):
    """Pfad und geschriebener Inhalt aus der Tool-Eingabe (Write, Edit, MultiEdit)."""
    path = tool_input.get("file_path", "") or ""
    if "content" in tool_input:
        return path, tool_input.get("content", "") or ""
    if "edits" in tool_input:
        parts = [e.get("new_string", "") or "" for e in tool_input.get("edits", [])]
        return path, "\n".join(parts)
    return path, tool_input.get("new_string", "") or ""


def has_skip_reason(lines, idx) -> bool:
    """Ein Kommentar in der Zeile davor oder dahinter genügt als Begründung."""
    for j in (idx - 1, idx + 1):
        if 0 <= j < len(lines) and ("//" in lines[j] or "/*" in lines[j]
                                    or lines[j].strip()[:1] == "*"):
            return True
    return False


def check(content, kind):
    out = []
    lines = content.splitlines()
    assert_re = TS_ASSERT if kind == "ts" else JAVA_ASSERT
    taut_re = TS_TAUTOLOGY if kind == "ts" else JAVA_TAUTOLOGY
    skip_re = TS_SKIP if kind == "ts" else JAVA_SKIP

    if not HAS_TEST_BODY.search(content):
        return out  # Helfer- oder Fixture-Datei ohne Test-Rümpfe

    if not assert_re.search(content):
        out.append(
            "Testdatei ohne jede Assertion (expect/assert/verify/assertThat) — ein Test, "
            "der nichts prüft, gibt falsche Sicherheit. Echte Assertion ergänzen."
        )

    taut = taut_re.search(content)
    if taut:
        out.append(
            f"Tautologische Assertion (`{taut.group(0)[:40]}`) — prüft sich selbst statt "
            "das Verhalten. Gegen den echten erwarteten Wert prüfen."
        )

    for i, ln in enumerate(lines):
        if SECRET_LIKE.search(ln) and not SECRET_ALLOW.search(ln):
            out.append(
                f"Secret-artiges Literal in der Testdatei (Zeile {i + 1}) — keine echten "
                "Tokens oder Schlüssel in Fixtures ablegen; Test-Konstante nutzen."
            )
            break

    for i, ln in enumerate(lines):
        if skip_re.search(ln) and not has_skip_reason(lines, i):
            out.append(
                f"Übersprungener Test ohne Begründung (Zeile {i + 1}) — `skip` bzw. "
                "`@Disabled` braucht einen Kommentar WARUM, sonst verschwindet die "
                "Abdeckung still."
            )
            break

    return out


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if not isinstance(data, dict) or data.get("tool_name") not in ("Edit", "Write", "MultiEdit"):
        sys.exit(0)
    path, content = extract(data.get("tool_input", {}) or {})
    if not path:
        sys.exit(0)
    is_test, kind = is_test_file(path)
    if not is_test:
        sys.exit(0)
    findings = check(content, kind)
    if findings:
        print(
            "Test-Qualitäts-Befunde in der letzten Änderung — bitte beheben:\n- "
            + "\n- ".join(findings),
            file=sys.stderr,
        )
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    try:
        use_utf8_stdio()  # Claude Code spricht UTF-8, Windows-Python sonst cp1252
        main()
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)  # fail-open
