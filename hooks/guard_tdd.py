#!/usr/bin/env python3
"""Stop-Wächter: meldet eine Logik-Änderung, die ohne Test im Change-Set steht.
Sprach- und stack-neutral.

Warum am Turn-Ende und nicht bei jedem Edit: Test und Quellcode wandern in getrennten
Schreibvorgängen. Erst am Turn-Ende ist das Change-Set vollständig — was dann ohne Test
dasteht, steht wirklich ohne Test da.

EHRLICHE GRENZE: dieser Wächter sieht nur, OB ein Test im Change-Set liegt — nie, ob er
zuerst geschrieben wurde und einmal rot war. Reihenfolge und Absicht sind nach dem Fakt
nicht messbar. Die Rot-zuerst-Disziplin und der Rot-Beleg bleiben Sache des Bearbeiters;
dieser Wächter ist nur der deterministische Boden darunter.

Melde-Semantik: exit 2 hält den Turn EINMAL pro Change-Set an (`stop_hook_active` lässt
den zweiten Anlauf durch, also keine Endlosschleife bei einem echten Refactor). Der
Bearbeiter muss die Meldung sehen und aktiv entscheiden: Test nachziehen oder als reines
Refactor bewusst durchwinken.

Fingerprint-Dedupe: zusätzlich wird ein Fingerabdruck über die sortierte beanstandete
Datei-Liste in `<Agenten-Ordner>/state/tdd-fingerprint` abgelegt. Ist er gegenüber dem letzten
Lauf unverändert (dieselbe ungedeckte Logik), bleibt der Wächter im nächsten Turn
komplett still — er nervt nicht Turn für Turn über dieselbe offene Stelle. Ändert sich
die Liste, meldet er wieder voll. Ein sauberes Change-Set löscht den Fingerabdruck.

Deckung wird PRO Logik-Datei geprüft, nicht global: ein Test irgendwo im Change-Set
befriedigt nicht jede unverwandte Logik-Änderung, sonst ist jeder Turn falsch grün, der
nebenbei einen fremden Test anfasst.

Wenig Fehlalarm: gemeldet werden nur verbreitete Logik-Quellflächen. Konfiguration,
Migrationen, generierter Code, Typ-Deklarationen, Build-Ausgaben, Werkzeug-Sandkästen,
der eigene Agenten-Ordner des Harness, Styles und Dokumentation sind ausgenommen;
unbekannte Endungen ebenfalls.
Fail-open bei jedem Eigenfehler.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

try:
    from hook_util import is_subagent_stop
except Exception:  # Helfer fehlt -> als Hauptthread behandeln, nie den Wächter brechen
    def is_subagent_stop(_data):
        return False

try:
    from hook_util import use_utf8_stdio
except Exception:  # Helfer fehlt -> dieselbe Umstellung lokal, die Meldung muss lesbar bleiben
    def use_utf8_stdio():
        for stream in (sys.stdin, sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

# Test-Marker über Ökosysteme hinweg.
TEST_SUFFIXES = (
    ".test.ts", ".test.tsx", ".test.js", ".test.jsx", ".test.mjs",
    ".spec.ts", ".spec.tsx", ".spec.js", ".spec.jsx",
    ".test.py", "_test.py", ".test.go", "_test.go",
    ".test.rb", "_test.rb", "_spec.rb",
    "test.java", "tests.java", "test.kt", "tests.kt",
    ".test.cs", "tests.cs", ".test.rs",
)

# Endungen, hinter denen Logik stecken kann.
LOGIC_EXT = (
    ".ts", ".tsx", ".js", ".jsx", ".mjs",
    ".java", ".kt", ".py", ".go", ".rb", ".rs", ".cs", ".php", ".swift",
)

# Pfad-Fragmente, die eine Datei trotz Logik-Endung nicht als Logik zählen lassen.
# Verglichen wird gegen `/<rel>`, damit ein Fragment auch direkt an der Repo-Wurzel greift.
EXEMPT_FRAGMENTS = (
    "/migrations/", "/migration/", "/generated/", "/__generated__/",
    "/node_modules/", "/vendor/", "/dist/", "/build/", "/.next/",
    "/config/", ".config.", "/scripts/",
    "/coverage/", "/.pytest_cache/", "/target/", "/out/",
)

EXEMPT_SUFFIXES = (
    ".d.ts", ".config.ts", ".config.js", ".config.mjs",
    ".stories.tsx", ".stories.ts",
)

# Ablage des Fingerabdrucks (per Umgebungsvariable überschreibbar).
FP_STATE_ENV = "SCRATCHPAD_TDD_STATE_FILE"


def _agent_dir() -> str:
    """Name des Agenten-Ordners, aus der eigenen Lage gelesen.

    Der Wächter liegt nach der Installation unter `<projekt>/<agenten-ordner>/hooks/`.
    Damit stimmt die Ablage in jedem Ordner, den der Nutzer gewählt hat — ohne dass
    irgendwo ein Werkzeugname fest verdrahtet wäre.
    """
    hooks_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.basename(os.path.dirname(hooks_dir)) or ".claude"


AGENT_DIR = _agent_dir()

FP_DEFAULT = os.path.join(AGENT_DIR, "state", "tdd-fingerprint")

MAX_LISTED = 12


def is_test(rel) -> bool:
    low = rel.lower()
    if low.endswith(TEST_SUFFIXES):
        return True
    base = low.replace("\\", "/").rsplit("/", 1)[-1]
    # Datei-Präfixe: pytest-Default `test_*.py`, `conftest.py`, generisch `spec_*`.
    if base.startswith("test_") or base.startswith("spec_") or base == "conftest.py":
        return True
    return (
        "/src/test/" in rel
        or "/tests/" in low
        or "/__tests__/" in low
        or "/spec/" in low
    )


def is_harness_path(rel) -> bool:
    """Liegt die Datei im eigenen Agenten-Ordner an der Projekt-Wurzel?

    Dort liegen nach der Installation die Wächter selbst (`<agenten-ordner>/hooks/*.py`).
    In einem frischen Projekt ohne Commit sind sie untracked und stünden sonst als
    ungetestete Logik im Change-Set — Werkzeug-Infrastruktur, kein Produktcode. Der
    Vergleich läuft über den Namen, aus der eigenen Lage gelesen, also unabhängig vom
    Commit-Stand und vom gewählten Ordner. Nur die Wurzel-Ebene zählt: ein gleichnamiger
    Ordner tiefer im Baum bleibt Produktcode.
    """
    head, sep, _ = rel.replace("\\", "/").partition("/")
    return bool(sep) and head.lower() == AGENT_DIR.lower()


def is_exempt_path(rel) -> bool:
    """Werkzeug-Sandkasten, Build-Ausgabe, generierter Code — weder Logik noch Test."""
    if is_harness_path(rel):
        return True
    low = "/" + rel.replace("\\", "/").lower()
    return any(frag in low for frag in EXEMPT_FRAGMENTS)


def is_logic(rel) -> bool:
    low = rel.lower()
    if not low.endswith(LOGIC_EXT):
        return False
    if low.endswith(EXEMPT_SUFFIXES):
        return False
    return not is_exempt_path(rel)


# --- Deckung: welcher Test gehört zu welcher Logik-Datei? ---------------------
#
# Drei sprach-neutrale Konventionen, eine genügt:
#   1. Datei-Stamm: `rechnung.py` zu `rechnung_test.py` / `test_rechnung.py` /
#      `RechnungTest.java`
#   2. Co-Location: der Test liegt im selben Verzeichnis
#   3. Gespiegelter Baum: gleicher Verzeichnis-Rest hinter einer Quell- oder Test-Wurzel
#      (`src/main/java/a/b/` zu `src/test/java/a/b/`, `src/a/b/` zu `tests/a/b/`)
# Bewusst grosszügig: der Boden soll auf echt ungedeckte Logik zeigen, nicht auf ein
# abweichendes Layout.

TREE_ROOTS = (
    "/src/main/java/", "/src/test/java/", "/src/main/kotlin/", "/src/test/kotlin/",
    "/src/main/scala/", "/src/test/scala/", "/src/main/", "/src/test/",
    "/src/", "/tests/", "/test/", "/spec/", "/__tests__/",
)

# Affixe, die einen Testdatei-Namen von der geprüften Einheit trennen.
TEST_AFFIXES = ("test", "tests", "spec", "specs")


def _stem(rel) -> str:
    """Datei-Stamm ohne Endung und ohne Test-Affix (`useFoo.test.ts` -> `usefoo`)."""
    base = rel.replace("\\", "/").rsplit("/", 1)[-1].lower()
    base = base.split(".", 1)[0] if "." in base else base
    for affix in TEST_AFFIXES:
        for sep in ("_", "-", "."):
            if base.startswith(affix + sep):
                base = base[len(affix) + 1:]
            if base.endswith(sep + affix):
                base = base[: -(len(affix) + 1)]
        if base.endswith(affix) and len(base) > len(affix):
            base = base[: -len(affix)]
    return base.strip("_-.")


def _dir(rel) -> str:
    norm = rel.replace("\\", "/")
    return norm.rsplit("/", 1)[0] if "/" in norm else ""


def _tree_tail(rel) -> str:
    """Verzeichnis-Rest hinter der ersten Quell- oder Test-Wurzel — macht gespiegelte
    Bäume vergleichbar. Ohne erkennbare Wurzel: leer (kein Spiegel-Signal)."""
    norm = "/" + rel.replace("\\", "/")
    for root in TREE_ROOTS:
        idx = norm.find(root)
        if idx >= 0:
            return _dir(norm[idx + len(root):])
    return ""


def _stems_match(logic_stem, test_stem) -> bool:
    if not logic_stem or not test_stem or min(len(logic_stem), len(test_stem)) < 3:
        return False
    return logic_stem in test_stem or test_stem in logic_stem


def is_covered(rel, tests) -> bool:
    """Trägt das Change-Set einen zu DIESER Logik-Datei passenden Test?"""
    logic_stem = _stem(rel)
    logic_dir = _dir(rel)
    logic_tail = _tree_tail(rel)
    for test in tests:
        if _stems_match(logic_stem, _stem(test)):
            return True
        if _dir(test) == logic_dir:
            return True
        if logic_tail and _tree_tail(test) == logic_tail:
            return True
    return False


# --- Fingerprint-Dedupe ------------------------------------------------------


def fingerprint_path(root: str) -> str:
    override = os.environ.get(FP_STATE_ENV)
    return override if override else os.path.join(root, FP_DEFAULT)


def compute_fingerprint(uncovered) -> str:
    joined = "\n".join(sorted(uncovered))
    return hashlib.sha256(joined.encode("utf-8", "replace")).hexdigest()


def read_stored_fingerprint(path: str):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read().strip()
    except Exception:
        return None


def store_fingerprint(path: str, value: str) -> None:
    try:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(value)
    except Exception:
        pass  # fail-open — ein Persistenz-Defekt darf den Boden nicht brechen


def clear_fingerprint(path: str) -> None:
    try:
        os.remove(path)
    except OSError:
        pass


def changed_files(root):
    """Das Change-Set des Arbeitsverzeichnisses; bei jedem Fehler leer (fail-open)."""
    try:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "-uall"],
            cwd=root, capture_output=True, text=True, timeout=5,
        )
    except Exception:
        return []
    files = []
    for line in proc.stdout.splitlines():
        rel = line[3:].strip() if len(line) > 3 else ""
        if " -> " in rel:  # Umbenennung: das Ziel zählt
            rel = rel.split(" -> ", 1)[1]
        if rel:
            files.append(rel.strip('"'))
    return files


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if is_subagent_stop(data):
        sys.exit(0)  # die Meldung adressiert den Hauptthread, nicht den Subagenten
    if data.get("stop_hook_active"):
        sys.exit(0)  # Schleifen-Schutz: schon gemeldet -> zweiten Anlauf durchlassen
    root = os.getcwd()

    logic, tests = [], []
    for rel in changed_files(root):
        if is_exempt_path(rel):
            continue
        if is_test(rel):
            tests.append(rel)
        elif is_logic(rel):
            logic.append(rel)

    uncovered = [rel for rel in logic if not is_covered(rel, tests)]

    fp_path = fingerprint_path(root)
    if not uncovered:
        clear_fingerprint(fp_path)  # sauber -> eine Wiedereinführung meldet wieder
        sys.exit(0)

    current_fp = compute_fingerprint(uncovered)
    if read_stored_fingerprint(fp_path) == current_fp:
        sys.exit(0)  # unveränderte Liste -> schon gemeldet -> still
    store_fingerprint(fp_path, current_fp)

    shown = uncovered[:MAX_LISTED]
    more = (f"\n  … und {len(uncovered) - len(shown)} weitere"
            if len(uncovered) > len(shown) else "")
    print(
        "TDD-Boden: Logik-Änderung ohne passenden Test im Change-Set:\n- "
        + "\n- ".join(shown) + more
        + "\nPflicht bei Bugs und Feature-Logik: zuerst ein fehlschlagender Test (rot), "
        "dann der Code bis grün — mit Rot-Beleg in der Rückgabe.\n"
        "Reines Refactor ohne Verhaltensänderung? Dann genügt, dass die bestehenden Tests "
        "grün bleiben — diese Meldung bewusst durchwinken.",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    try:
        use_utf8_stdio()  # Claude Code spricht UTF-8, Windows-Python sonst cp1252
        main()
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)  # fail-open
