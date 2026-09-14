#!/usr/bin/env bash
# Installiert scratchpad in ein Zielprojekt.
# Aufruf: bash install.sh <pfad-zum-zielprojekt> [neutral|codex|claude]
set -euo pipefail

QUELLE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ $# -lt 1 ] || [ -z "${1:-}" ]; then
  echo "FEHLER: Pfad des Zielprojekts fehlt." >&2
  echo "Aufruf: bash install.sh <pfad-zum-zielprojekt> [neutral|codex|claude]" >&2
  exit 1
fi
ZIEL="$1"
MODUS="${2:-}"
if [ $# -gt 2 ]; then echo "FEHLER: Zu viele Argumente." >&2; exit 1; fi
if [ -z "$MODUS" ]; then printf 'Zielmodus (neutral, codex, claude): '; IFS= read -r MODUS; fi
MODUS="${MODUS,,}"
case "$MODUS" in neutral|codex|claude) ;; *) echo "FEHLER: Unbekannter Zielmodus: $MODUS (erlaubt: neutral, codex, claude)" >&2; exit 1;; esac

mkdir -p "$ZIEL"
ZIEL="$(cd "$ZIEL" && pwd)"
PYTHON="$(command -v python3 || command -v python || true)"

kopiere_ordner() { mkdir -p "$2"; cp -R "$QUELLE/$1/." "$2/"; echo "  kopiert: $1 -> ${2#$ZIEL/}"; }
kopiere_datei() { mkdir -p "$(dirname "$2")"; cp "$QUELLE/$1" "$2"; echo "  kopiert: $1 -> ${2#$ZIEL/}"; }
ersetze_platzhalter() {
  local basis="$1" ordner="$2" datei
  while IFS= read -r -d '' datei; do
    ORDNER="$ordner" perl -0777 -i -pe 's/\Q<AGENTENORDNER>\E/$ENV{ORDNER}/g' "$datei"
  done < <(find "$basis" -type f \( -name '*.md' -o -name '*.json' -o -name '*.py' \) -print0)
}
installiere_kern() {
  kopiere_ordner kern "$1/vorgehen"
  kopiere_datei vorlagen/tasks-README.md "$1/tasks/README.md"
  kopiere_datei agent/AGENTS-block.md "$1/INSTRUCTIONS.md"
  ersetze_platzhalter "$1" "$2"
}

echo "Installiere Scratchpad ($MODUS) nach: $ZIEL"
case "$MODUS" in
  neutral) installiere_kern "$ZIEL/.agents" .agents ;;
  codex)
    BASIS="$ZIEL/.agents"; installiere_kern "$BASIS" .agents; kopiere_ordner agent/skills "$BASIS/skills"
    START='<!-- scratchpad:start -->'; ENDE='<!-- scratchpad:end -->'; AGENTS="$ZIEL/AGENTS.md"
    if ! grep -Fq "$START" "$AGENTS" 2>/dev/null; then
      { [ ! -e "$AGENTS" ] || printf '\n'; printf '%s\n' "$START"; cat "$BASIS/INSTRUCTIONS.md"; printf '\n%s\n' "$ENDE"; } >> "$AGENTS"
      echo "  ergaenzt: AGENTS.md (Scratchpad-Block)"
    else echo "  unveraendert: AGENTS.md (Scratchpad-Block bereits vorhanden)"; fi
    ;;
  claude)
    BASIS="$ZIEL/.claude"
    kopiere_ordner kern "$BASIS/vorgehen"; kopiere_ordner agent/commands "$BASIS/commands"; kopiere_ordner agent/skills "$BASIS/skills"
    mkdir -p "$BASIS/hooks"
    for datei in "$QUELLE"/hooks/*.py; do [ -e "$datei" ] || continue; case "$(basename "$datei")" in test_*.py) continue;; esac; cp "$datei" "$BASIS/hooks/"; done
    kopiere_datei vorlagen/tasks-README.md "$BASIS/tasks/README.md"; kopiere_datei kern/antwortform.md "$BASIS/output-styles/scratchpad-projektleiter.md"
    if [ -z "$PYTHON" ]; then echo "FEHLER: python3/python nicht gefunden." >&2; exit 1; fi
    [ -f "$BASIS/settings.json" ] || printf '{}\n' > "$BASIS/settings.json"
    "$PYTHON" "$QUELLE/install_settings.py" "$BASIS/settings.json" scratchpad-projektleiter "$QUELLE/agent/settings-hooks.json" .claude
    ersetze_platzhalter "$BASIS" .claude
    ;;
esac
echo "Fertig. Scratchpad installiert ($MODUS)."
