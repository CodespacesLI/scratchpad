#!/usr/bin/env python3
"""Stop-Wächter: misst den Kontextstand der Sitzung und meldet, wenn er über dem Budget
steht — im Default als einmalige Warnung, mit gesetztem Schalter als Auflage pro Turn.

Warum überhaupt: der Kontext wächst still. Jeder Folge-Turn liest den ganzen bisherigen
Verlauf erneut, wird also teurer und zugleich schlechter — und beim Abriss ist der Stand
weg, wenn ihn niemand destilliert hat. Auf den Zähler zu schauen ist Handdisziplin an
genau der Stelle, an der in langen Sitzungen niemand hinschaut. Dieser Wächter ersetzt
das Hinschauen durch eine Messung.

Gemessen wird die letzte NICHT-Sidechain-`assistant`-Zeile des Transcripts, Summe von
`input_tokens + cache_read_input_tokens + cache_creation_input_tokens + output_tokens`.
Die eigene Ausgabe zählt bewusst mit: sie steht im nächsten Turn wieder im Fenster.
Sidechain-Zeilen (Subagenten-Nachrichten, die im Haupt-Transcript mitlaufen) werden
übersprungen — sie sind der Kontext eines Agenten, nicht der dieser Sitzung.

Zwei Stufen, umgeschaltet per Umgebungsvariable:

* **Default (Schalter aus): warnen, einmal pro Sitzung.** Über der Schwelle meldet der
  Wächter exit 2 mit der Empfehlung, JETZT `/handoff` zu fahren und danach `/clear` +
  `/resume`. Eine Stempel-Datei hält die Sitzungs-Kennung fest; Folge-Turns derselben
  Sitzung bleiben still. Der Mensch entscheidet — ein erzwungener Handoff mitten in
  einer Diskussion wäre Bevormundung.
* **Schalter an (`SCRATCHPAD_AUTO_HANDOFF=1`): erzwingen, in jedem Turn.** Der Turn endet
  mit der Auflage, SOFORT `/handoff` zu fahren, also den Brief nach
  `<Agenten-Ordner>/state/handoff-brief.md` zu schreiben. `/clear` und `/resume` bleiben
  Handarbeit — das kann ein Wächter technisch nicht auslösen, und das ist die ehrliche
  Grenze des Werkzeugs, kein Fehler. Der Wächter startet NICHTS von selbst: keine
  Nachfolge-Sitzung, kein Fenster, kein Skript. Er misst und sagt, was jetzt zu tippen ist.

Endlos-Block-Schutz im Auto-Modus: wurde der Handoff-Brief IN DIESEM Turn geschrieben,
bleibt der Wächter still. Der Turn wird dafür aus dem Transcript rekonstruiert (rückwärts
bis zum letzten Prompt des Menschen) — sonst blockte die Auflage genau den Turn, der sie
erfüllt.

Schwelle per `SCRATCHPAD_KONTEXT_BUDGET` (ganze Zahl) überschreibbar; kaputter Wert →
Konstante. Für eine Vorführung lässt sich die Schwelle damit in einer Terminal-Zeile auf
z.B. 20000 senken.

STILL (exit 0) ausserdem: `stop_hook_active` (Loop-Schutz), Subagenten-Stop (die Auflage
adressiert den Hauptthread), und fail-open bei jedem Eigenfehler — kaputtes stdin,
fehlendes/unlesbares/unparsebares Transcript, kein `usage`-Block. Ein Wächter darf einen
Turn nie wegen eigener Defekte anhalten.
"""
from __future__ import annotations

import json
import os
import sys

try:
    from hook_util import is_subagent_stop, iter_lines_reverse
except Exception:  # Helfer fehlt/kaputt -> nicht messbar -> fail-open, nie blocken
    def is_subagent_stop(_data):
        return False

    iter_lines_reverse = None

# Umgebungsvariablen: Schwelle, Schalter, Ablage-Überschreibungen.
ENV_BUDGET = "SCRATCHPAD_KONTEXT_BUDGET"
ENV_AUTO = "SCRATCHPAD_AUTO_HANDOFF"
ENV_AGENT_DIR = "SCRATCHPAD_AGENT_DIR"
ENV_STEMPEL_FILE = "SCRATCHPAD_KONTEXT_STEMPEL"

# Kontext-Grenze der Sitzung. Nur absenken, nie anheben, um einen unbequemen Turn
# durchzuwinken — der Ausweg ist der Handoff, nicht die Schwelle.
THRESHOLD = 150_000

# Felder, die zusammen den Stand des Fensters ergeben (Begründung im Modul-Kopf).
CONTEXT_USAGE_FIELDS = (
    "input_tokens",
    "cache_read_input_tokens",
    "cache_creation_input_tokens",
    "output_tokens",
)

# Treiber-Zweig: liegt der Marker (legt `treiber.py` beim Lauf-Start, raeumt er am Ende),
# sitzt niemand vor der Sitzung — `/clear` + `/resume` sind interaktive Schritte, die eine
# headless Sitzung nicht gehen kann. Die Auto-Auflage nennt dann den Treiber-Weg: Brief
# schreiben, Turn beenden, der Treiber startet die naechste Runde. Geprueft wird nur die
# EXISTENZ der Datei — Schwelle, Messung und fail-open bleiben unveraendert.
TREIBER_MARKER_NAME = "treiber-aktiv"

WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
PATH_KEYS = ("file_path", "notebook_path")


def _eigener_agent_dir() -> str:
    """Name des Agenten-Ordners, aus der eigenen Lage gelesen.

    Der Wächter liegt nach der Installation unter `<projekt>/<agenten-ordner>/hooks/`.
    Damit stimmen Stempel- und Brief-Pfad in jedem Ordner, den der Nutzer gewählt hat —
    ohne dass irgendwo ein Werkzeugname fest verdrahtet wäre.
    """
    hooks_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.basename(os.path.dirname(hooks_dir)) or ".claude"


DEFAULT_AGENT_DIR = _eigener_agent_dir()
STEMPEL_DEFAULT = os.path.join(DEFAULT_AGENT_DIR, "state", "kontext-budget-stempel")
HANDOFF_SUFFIX = "state/handoff-brief.md"


def agent_dir() -> str:
    return os.environ.get(ENV_AGENT_DIR) or DEFAULT_AGENT_DIR


def handoff_brief_pfad() -> str:
    return agent_dir().replace("\\", "/").rstrip("/") + "/" + HANDOFF_SUFFIX


def project_root() -> str:
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def stempel_datei(root: str) -> str:
    override = os.environ.get(ENV_STEMPEL_FILE)
    if override:
        return override
    return os.path.join(root, agent_dir(), "state", "kontext-budget-stempel")


def resolve_threshold() -> int:
    """Schwelle aus der Umgebungsvariable, sonst die Konstante. Kaputter Wert → Konstante."""
    raw = os.environ.get(ENV_BUDGET)
    if not raw:
        return THRESHOLD
    try:
        value = int(str(raw).strip())
    except (TypeError, ValueError):
        return THRESHOLD
    return value if value > 0 else THRESHOLD


def auto_handoff() -> bool:
    return str(os.environ.get(ENV_AUTO, "")).strip() == "1"


def kontext_summe(path):
    """Kontext-Summe der letzten NICHT-Sidechain-assistant-Zeile, sonst None.

    Gelesen wird rückwärts vom Dateiende (`iter_lines_reverse`): Transcripts werden
    megabyte-gross, ein Voll-Read wäre pro Turn-Ende bezahlte Zeit. Kaputte oder
    abgeschnittene Zeilen werden übersprungen; bool- und Nicht-int-Werte zählen nicht mit.
    """
    if iter_lines_reverse is None:
        return None
    for line in iter_lines_reverse(path):
        try:
            entry = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue  # abgeschnittene/kaputte Zeile — weiter nach oben laufen
        if not isinstance(entry, dict) or entry.get("type") != "assistant":
            continue
        if entry.get("isSidechain"):
            continue  # Subagenten-Nachricht — nicht der Kontext dieser Sitzung
        message = entry.get("message")
        if not isinstance(message, dict):
            continue
        usage = message.get("usage")
        if not isinstance(usage, dict):
            continue
        total = 0
        for field in CONTEXT_USAGE_FIELDS:
            value = usage.get(field, 0)
            if isinstance(value, bool) or not isinstance(value, int):
                continue
            total += value
        return total
    return None


# --- Turn-Rekonstruktion (Endlos-Block-Schutz) --------------------------------


def _written_paths(entry: dict) -> list:
    """Dateipfade, die dieser assistant-Eintrag per Schreib-Werkzeug anfasst."""
    if not isinstance(entry, dict) or entry.get("type") != "assistant":
        return []
    message = entry.get("message")
    if not isinstance(message, dict):
        return []
    content = message.get("content")
    if not isinstance(content, list):
        return []
    out = []
    for block in content:
        if not isinstance(block, dict) or block.get("type") != "tool_use":
            continue
        if block.get("name") not in WRITE_TOOLS:
            continue
        payload = block.get("input")
        if not isinstance(payload, dict):
            continue
        for key in PATH_KEYS:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                out.append(value.strip())
                break
    return out


def _is_human_prompt(entry: dict) -> bool:
    """True nur für einen echten Prompt des Menschen — das ist die Turn-Grenze.

    Werkzeug-Ergebnisse liegen im Transcript ebenfalls als `type == user`, tragen aber
    keinen Text-Block; Meta- und Sidechain-Einträge (Subagenten-Aufträge) sind keine
    Prompts des Menschen.
    """
    if not isinstance(entry, dict) or entry.get("type") != "user":
        return False
    if entry.get("isMeta") or entry.get("isSidechain"):
        return False
    message = entry.get("message")
    if not isinstance(message, dict) or message.get("role") != "user":
        return False
    content = message.get("content")
    if isinstance(content, str):
        return bool(content.strip())
    if isinstance(content, list):
        return any(
            isinstance(block, dict) and block.get("type") == "text"
            and str(block.get("text", "")).strip()
            for block in content
        )
    return False


def brief_im_turn_geschrieben(transcript_path) -> bool:
    """Wurde der Handoff-Brief im laufenden Turn geschrieben?

    Gelesen wird rückwärts bis zum letzten Prompt des Menschen — das ist die Turn-Grenze.
    Ein Brief aus einem früheren Turn zählt nicht: sonst löste ein alter Handoff den
    Wächter für immer ab.
    """
    if iter_lines_reverse is None:
        return False
    if not transcript_path or not isinstance(transcript_path, str):
        return False
    if not os.path.isfile(transcript_path):
        return False
    ziel = HANDOFF_SUFFIX
    try:
        for line in iter_lines_reverse(transcript_path):
            try:
                entry = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                continue
            if _is_human_prompt(entry):
                return False  # Turn-Grenze erreicht, kein Brief darin
            for path in _written_paths(entry):
                if path.replace("\\", "/").rstrip("/").endswith(ziel):
                    return True
    except OSError:
        return False
    return False


# --- Stempel (einmalige Warnung pro Sitzung) ----------------------------------


def stempel_lesen(path: str):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return None


def stempel_schreiben(path: str, wert: str) -> None:
    """Sitzungs-Kennung ablegen; scheitert das, wird höchstens einmal zu viel gewarnt."""
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(wert)
    except OSError:
        pass


def treiber_aktiv(root: str) -> bool:
    """True, wenn ein Treiber-Lauf laeuft. Jeder Defekt heisst False → bisherige Meldung."""
    try:
        return os.path.isfile(os.path.join(root, agent_dir(), "state", TREIBER_MARKER_NAME))
    except Exception:
        return False


def build_message(total: int, threshold: int, auto: bool, treiber: bool = False) -> str:
    """Ein Absatz: wo wir stehen, was jetzt zu tun ist."""
    stand = (f"[Kontext-Budget] Diese Sitzung steht bei ~{total // 1000}k Tokens Kontext, "
             f"über der Grenze von {threshold // 1000}k.")
    if auto and treiber:
        return (
            f"{stand} Ein Treiber-Lauf ist aktiv: schreibe JETZT den Handoff-Brief nach "
            f"{handoff_brief_pfad()} (destillierter Stand, offene Punkte, Belege) und "
            "beende dann deinen Turn — der Treiber startet automatisch eine frische "
            "Sitzung, die den Brief liest. Keine neue Arbeit mehr in diesem Kontext."
        )
    if auto:
        return (
            f"{stand} Auto-Handoff ist eingeschaltet: fahre JETZT /handoff und schreibe "
            f"den Brief nach {handoff_brief_pfad()} (destillierter Stand, offene Punkte, "
            "Belege) — keine neue Arbeit mehr in diesem Kontext. Danach /clear, danach "
            "/resume: diese beiden Schritte tippt der Mensch selbst, auslösen kann ein "
            "Wächter sie nicht."
        )
    return (
        f"{stand} Empfiehl dem User JETZT /handoff (destillierter Stand nach "
        f"{handoff_brief_pfad()}), danach /clear und /resume. Ein aufgeblähter Kontext "
        "ist teurer und schlechter, und ein Abriss ohne Brief kostet den ganzen Stand. "
        "Diese Meldung kommt in dieser Sitzung nur einmal."
    )


def _stderr_robust() -> None:
    """Nicht darstellbare Zeichen ersetzen statt die Meldung zu verlieren.

    Kann die Codepage des Systems ein Zeichen der Meldung nicht schreiben, würde der
    Schreibversuch scheitern — und der Wächter fiele still auf fail-open zurück, obwohl er
    etwas zu sagen hat.
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
        return 0  # Die Auflage adressiert den Hauptthread, nicht den Subagenten

    transcript = data.get("transcript_path")
    if not isinstance(transcript, str) or not transcript or not os.path.isfile(transcript):
        return 0  # kein messbares Transcript -> fail-open

    try:
        total = kontext_summe(transcript)
    except Exception:
        return 0  # Lese-/Parse-Fehler -> fail-open
    if total is None:
        return 0  # kein usage-Block -> Stand nicht messbar -> fail-open

    threshold = resolve_threshold()
    if total < threshold:
        return 0

    root = project_root()
    if auto_handoff():
        try:
            if brief_im_turn_geschrieben(transcript):
                return 0  # Auflage in diesem Turn erfüllt -> nicht endlos blocken
        except Exception:
            pass  # Rekonstruktion unsicher -> lieber melden als still bleiben
        _stderr_robust()
        print(build_message(total, threshold, True, treiber_aktiv(root)), file=sys.stderr)
        return 2

    session = str(data.get("session_id") or "")
    stempel = stempel_datei(root)
    if session and stempel_lesen(stempel) == session:
        return 0  # in dieser Sitzung schon gemeldet
    stempel_schreiben(stempel, session)
    _stderr_robust()
    print(build_message(total, threshold, False), file=sys.stderr)
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)  # fail-open — nie einen Turn wegen eigener Defekte anhalten
