#!/usr/bin/env python3
"""Stop-Wächter: meldet die still verschwundene Task-Zeile aus einem Bauplan.

Ein Bauplan liegt unter `.claude/tasks/<slug>.md` und trägt im Kopf eine Status-Zeile
(`Status: entwurf` / `im-bau` / `fertig`). Die Regel lautet: abgesprochene Plan-Punkte
nie stillschweigend kürzen — umgesetzt wird abgehakt, verworfen wird BEGRÜNDET gestrichen
und dem Menschen gesagt.

**Der Wächter misst genau diesen einen Vorgang** (bewusste Verengung): eine Task-Zeile
(`- [ ]` oder `- [x]`), die im Basis-Stand des Change-Sets noch da war, ist im aktuellen
Stand VERSCHWUNDEN, und derselbe Diff trägt keine Streichungs-Begründung. Das ist die
Kürzung selbst — nicht ihr Umfeld.

Was bewusst NICHT mehr meldet: offene Punkte an sich, Code-Schreiben ohne Plan-Berührung,
fehlende Akzeptanzkriterien, fehlende Checkbox-Formalisierung. Der alte „gebaut, aber Plan
nicht angefasst"-Verdacht stellte die weit überwiegende Mehrheit aller Warnungen und
belegte nie eine Kürzung: am Stück weiterarbeiten IST der Normalfall, und ein Plan wird am
Ende einer Arbeitsstrecke abgeglichen, nicht nach jedem Edit. Ein Sensor, der bei jedem
Turn-Ende dasselbe sagt, wird weggelesen — genau das sollte er nie werden. Mit dem Verdacht
entfallen auch der Zustands-Stempel, die Transcript-Rekonstruktion des Turns und die
Bezugs-Heuristik: ohne die Meldung haben sie keinen Gegenstand mehr.

Nicht-Fälle, die im Diff wie ein Verschwinden aussehen und darum ausdrücklich still sind:
  - **Abhaken** (`- [ ]` → `- [x]`): die Zeile bleibt, nur der Status wechselt.
  - **Umformulieren**: der Kern des Zeilentexts steht in einer hinzugefügten Zeile weiter.
  - **Entwurf**: ein Plan mit `Status: entwurf` ist noch nicht abgesprochen — dort kommen
    und gehen Zeilen legitim, geprüft werden nur `im-bau` und `fertig`.
  - **Ganz verschwundene Plan-Datei** (Archivierung): geprüft wird nur, was JETZT unter
    `.claude/tasks/*.md` liegt; der Glob steigt nicht in Unterordner (ein fertiger Plan
    unter `.claude/tasks/done/` ist damit ausser Reichweite).
  - **Begründete Streichung**: irgendeine im selben Diff hinzugefügte Zeile trägt
    `gestrichen`/`verworfen`/`entfällt`/`obsolet`/`ersetzt durch`/Durchstreichung `~~…~~`.

Basis des Vergleichs ist das Change-Set-Fenster: Upstream (sonst `HEAD`) gegen den
Arbeitsbaum — damit fällt ein in einem noch nicht gepushten Commit gestrichener Punkt
genauso auf wie ein ungespeicherter. Gemessen wird im TATSÄCHLICHEN Arbeitsbaum
(`git rev-parse --show-toplevel`), nicht über eine Umgebungsvariable — sonst liest der
Wächter bei Arbeit in einem zweiten Arbeitsbaum den falschen Checkout.

Warnt additiv (exit 2, ein Satz Problem + ein Satz Auflage), blockt nie dauerhaft.
Fail-open bei jedem Eigenfehler: kaputtes stdin, kein git, unlesbare Datei → still exit 0.
`stop_hook_active` verhindert die Endlosschleife.
"""
from __future__ import annotations

import glob
import json
import os
import re
import subprocess
import sys

try:
    from hook_util import is_subagent_stop
except Exception:  # Helfer fehlt -> als Hauptthread behandeln, nie den Wächter brechen
    def is_subagent_stop(_data):
        return False

# Ablage der Baupläne, per Umgebungsvariable überschreibbar.
# Baupläne liegen unter `.claude/tasks/<slug>.md`, fertige im Archiv `.claude/tasks/done/`.
ENV_TASKS_DIR = "SCRATCHPAD_TASKS_DIR"
DEFAULT_TASKS_DIR = ".claude/tasks"

GLOB_PATTERN = "*.md"
README_NAME = "README.md"

# Die Status-Zeile ist ein Vertrag mit dem Task-Format: genau diese Schreibweise.
STATUS_RE = re.compile(r"^\s*\**\s*Status\s*:\s*\**\s*([a-zäöü-]+)", re.IGNORECASE)
# Nur der Kopf des Plans trägt die Status-Zeile.
STATUS_HEAD_LINES = 25
# Ein Entwurf ist noch nicht abgesprochen — dort ist Streichen kein Wortbruch.
STATUS_UNGEPRUEFT = {"entwurf"}

# GitHub-Checkbox-Listeneintrag: `- [ ] Titel` / `* [x] Titel`.
CHECKBOX_RE = re.compile(r"^\s*[-*]\s+\[([ xX])\]\s*(.*)$")

# Streichungs-Begründung im selben Diff. Bewusst grosszügig: der Wächter will die
# BEGRÜNDUNG sehen, nicht eine bestimmte Formulierung erzwingen.
STRIKE_RE = re.compile(
    r"gestrichen|streiche|verworfen|entf[äa]llt|obsolet|hinf[äa]llig"
    r"|ersetzt durch|zur[üu]ckgestellt|nicht mehr (n[öo]tig|noetig|gebraucht|relevant)"
    r"|~~",
    re.IGNORECASE,
)

# Markdown-Zierrat und Satzzeichen raus, damit „**Task 2** — Guard" und „Task 2 - Guard"
# dieselbe Zeile sind.
_NOISE_RE = re.compile(r"[`*_#>~\[\]()]|[.,;:!?]|—|–")
_WS_RE = re.compile(r"\s+")

# Ab dieser Länge zählt Teil-Enthaltensein als „dieselbe Zeile, nur umformuliert".
# Darunter wäre die Verwechslungsgefahr zu gross (z.B. „offen" in „noch offen").
MIN_OVERLAP = 8
# So viele verschwundene Zeilen werden namentlich genannt (die Meldung bleibt kurz).
MAX_LISTED = 2
MAX_LABEL = 48
MAX_MESSAGE = 500
GIT_TIMEOUT = 10


def tasks_dir() -> str:
    return os.environ.get(ENV_TASKS_DIR) or DEFAULT_TASKS_DIR


def normalize(label: str) -> str:
    return _WS_RE.sub(" ", _NOISE_RE.sub("", label)).strip().lower()


def _git(root: str, *args: str) -> subprocess.CompletedProcess:
    """git-Aufruf mit fest auf UTF-8 gestellter Dekodierung.

    Ohne die feste Angabe dekodiert Python die Ausgabe mit der Landes-Codepage des
    Systems (unter Windows z.B. cp1252). Ein Gedankenstrich aus dem Bauplan käme dann als
    Zeichensalat an — und die entfernte Zeile sähe anders aus als die hinzugefügte,
    obwohl beide denselben Text tragen. Genau daraus entstünde ein Fehlalarm.
    """
    return subprocess.run(["git", *args], cwd=root, capture_output=True,
                          encoding="utf-8", errors="replace", timeout=GIT_TIMEOUT)


def worktree_root():
    """Wurzel des tatsächlichen Arbeitsbaums; `None`, wenn das Verzeichnis kein Repo ist.

    Ohne Repo gibt es kein Vorher/Nachher — der Wächter schweigt dann, statt zu raten.
    """
    try:
        proc = _git(os.getcwd(), "rev-parse", "--show-toplevel")
    except Exception:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def base_refs(root: str) -> list:
    """Basis-Stände des Change-Set-Fensters, in Reihenfolge: Upstream, sonst `HEAD`."""
    refs = []
    try:
        proc = _git(root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
        if proc.returncode == 0 and proc.stdout.strip():
            refs.append(proc.stdout.strip())
    except Exception:
        pass
    refs.append("HEAD")
    return refs


def plan_status(path: str):
    """Status aus dem Kopf der Plan-Datei, sonst None (unlesbar oder ohne Status-Zeile)."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for index, line in enumerate(fh):
                if index >= STATUS_HEAD_LINES:
                    break
                match = STATUS_RE.match(line)
                if match:
                    return match.group(1).strip().lower()
    except OSError:
        return None
    return None


def plan_files(root: str) -> list:
    """(rel_pfad, basename) der zu prüfenden Pläne; README und Entwürfe ausgenommen.

    Der Glob steigt bewusst NICHT in Unterordner (`*` matcht kein `/`) — das Archiv unter
    `.claude/tasks/done/` (und jeder andere Unterordner) bleibt damit unberührt.
    """
    out = []
    pattern = os.path.join(root, tasks_dir(), GLOB_PATTERN)
    for full in sorted(glob.glob(pattern)):
        base = os.path.basename(full)
        if base == README_NAME:
            continue
        if plan_status(full) in STATUS_UNGEPRUEFT:
            continue
        out.append((os.path.relpath(full, root).replace(os.sep, "/"), base))
    return out


def diff_lines(root: str, rel: str):
    """(entfernte, hinzugefügte) Roh-Zeilen der Datei über das Change-Set-Fenster.

    `None` = nicht bestimmbar (kein git, kein auflösbarer Basis-Stand, Fehler) → der
    Aufrufer schweigt. Eine verpasste Warnung ist billiger als eine geratene.
    """
    for base in base_refs(root):
        try:
            proc = _git(root, "diff", "-U0", base, "--", rel)
        except Exception:
            return None
        if proc.returncode != 0:
            continue  # Basis-Stand nicht auflösbar (z.B. Repo ohne Commit) -> nächster
        removed, added = [], []
        for line in proc.stdout.splitlines():
            if line.startswith("---") or line.startswith("+++"):
                continue
            if line.startswith("-"):
                removed.append(line[1:])
            elif line.startswith("+"):
                added.append(line[1:])
        return removed, added
    return None


def vanished_labels(removed: list, added: list) -> list:
    """Task-Zeilen, die weg sind — ohne die Abhak- und Umformulierungs-Fälle."""
    added_labels = [normalize(m.group(2)) for m in
                    (CHECKBOX_RE.match(ln) for ln in added) if m]
    out = []
    for line in removed:
        match = CHECKBOX_RE.match(line)
        if not match:
            continue
        label = normalize(match.group(2))
        if not label:
            continue
        if any(label == other
               or (len(label) >= MIN_OVERLAP and label in other)
               or (len(other) >= MIN_OVERLAP and other in label)
               for other in added_labels):
            continue  # abgehakt oder umformuliert — die Zeile lebt weiter
        out.append(match.group(2).strip() or label)
    return out


def build_message(hits: list) -> str:
    """Ein Satz Problem, ein Satz Auflage — keine Absätze."""
    count = len(hits)
    shown = "; ".join(f"{base}: {label[:MAX_LABEL]}" for base, label in hits[:MAX_LISTED])
    if count > MAX_LISTED:
        shown += f"; +{count - MAX_LISTED} weitere"
    subject = ("eine vereinbarte Task-Zeile ist" if count == 1
               else f"{count} vereinbarte Task-Zeilen sind")
    return (
        f"Plan-Drift: {subject} aus dem Bauplan verschwunden, ohne dass derselbe Diff die "
        f"Streichung begründet ({shown}). Hol die Zeile zurück, hak sie ab oder streich "
        "sie begründet im Plan (Wort gestrichen/verworfen in derselben Änderung) und sag "
        "es dem Menschen."
    )[:MAX_MESSAGE]


def _stderr_robust() -> None:
    """Nicht darstellbare Zeichen ersetzen statt die Meldung zu verlieren.

    Die Meldung trägt Umlaute und den Text aus dem Bauplan. Kann die Codepage des Systems
    ein Zeichen nicht schreiben, würde der Schreibversuch scheitern — und der Wächter fiele
    still auf fail-open zurück, obwohl er etwas zu sagen hat.
    """
    try:
        sys.stderr.reconfigure(errors="replace")
    except Exception:
        pass


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(data, dict):
        return 0
    if data.get("stop_hook_active"):
        return 0  # Loop-Schutz: in diesem Stop-Zyklus schon getriggert
    if is_subagent_stop(data):
        return 0  # Die Warnung adressiert den Hauptthread, nicht den Subagenten

    root = worktree_root()
    if not root:
        return 0

    hits = []
    for rel, base in plan_files(root):
        diff = diff_lines(root, rel)
        if diff is None:
            continue
        removed, added = diff
        if not removed:
            continue
        if any(STRIKE_RE.search(ln) for ln in added):
            continue  # Streichung ist im selben Diff begründet -> der erlaubte Weg
        hits.extend((base, label) for label in vanished_labels(removed, added))

    if not hits:
        return 0
    _stderr_robust()
    print(build_message(hits), file=sys.stderr)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)  # fail-open — nie einen Turn wegen eigener Defekte anhalten
