#!/usr/bin/env bash
# Testet alle Installer-Modi, Idempotenz und Bash/PowerShell-Paritaet.
set -euo pipefail
QUELLE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WURZEL="${1:-$(mktemp -d)}"
FEHLER=0
fehler() { echo "FEHLER: $*" >&2; FEHLER=$((FEHLER + 1)); }
datei() { [ -f "$1" ] || fehler "Datei fehlt: $1"; }
nicht_da() { [ ! -e "$1" ] || fehler "Darf nicht existieren: $1"; }
ausfuehren() { bash "$QUELLE/install.sh" "$1" "$2" > "$1.log" 2>&1 || fehler "Bash-Installation ($2) schlug fehl"; }
echo "== Testziel: $WURZEL"; mkdir -p "$WURZEL"

NEUTRAL="$WURZEL/neutral"; ausfuehren "$NEUTRAL" neutral
datei "$NEUTRAL/.agents/vorgehen/01-brainstorm.md"; datei "$NEUTRAL/.agents/tasks/README.md"; datei "$NEUTRAL/.agents/INSTRUCTIONS.md"
nicht_da "$NEUTRAL/.agents/skills"; nicht_da "$NEUTRAL/.claude"; nicht_da "$NEUTRAL/AGENTS.md"
grep -q '<AGENTENORDNER>' "$NEUTRAL/.agents/INSTRUCTIONS.md" && fehler 'neutral: Platzhalter blieb stehen'

CODEX="$WURZEL/codex"; mkdir -p "$CODEX"; printf '# Eigene Regeln\n\nNicht ueberschreiben.\n' > "$CODEX/AGENTS.md"
ausfuehren "$CODEX" codex; ausfuehren "$CODEX" codex
datei "$CODEX/.agents/vorgehen/03-build.md"; datei "$CODEX/.agents/tasks/README.md"; datei "$CODEX/.agents/INSTRUCTIONS.md"; datei "$CODEX/.agents/skills/grill-me/SKILL.md"
nicht_da "$CODEX/.claude"; grep -q 'Nicht ueberschreiben.' "$CODEX/AGENTS.md" || fehler 'codex: bestehende AGENTS.md-Inhalte verloren'
[ "$(grep -Fc '<!-- scratchpad:start -->' "$CODEX/AGENTS.md")" = 1 ] || fehler 'codex: Scratchpad-Block nicht idempotent'

CLAUDE="$WURZEL/claude"; mkdir -p "$CLAUDE/.claude"; printf '{"permissions":{"allow":["Bash(ls:*)"]}}' > "$CLAUDE/.claude/settings.json"
ausfuehren "$CLAUDE" claude; ausfuehren "$CLAUDE" claude
datei "$CLAUDE/.claude/vorgehen/01-brainstorm.md"; datei "$CLAUDE/.claude/commands/build.md"; datei "$CLAUDE/.claude/skills/grill-me/SKILL.md"; datei "$CLAUDE/.claude/hooks/guard_tdd.py"; datei "$CLAUDE/.claude/output-styles/scratchpad-projektleiter.md"; datei "$CLAUDE/.claude/tasks/README.md"
nicht_da "$CLAUDE/.agents"
python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); assert d["permissions"]["allow"]==["Bash(ls:*)"] and d["outputStyle"]=="scratchpad-projektleiter" and "hooks" in d' "$CLAUDE/.claude/settings.json" || fehler 'claude: settings.json wurde nicht korrekt gemerged'

INTERAKTIV="$WURZEL/interaktiv"; printf 'neutral\n' | bash "$QUELLE/install.sh" "$INTERAKTIV" > "$INTERAKTIV.log" 2>&1 || fehler 'interaktive Bash-Auswahl schlug fehl'; datei "$INTERAKTIV/.agents/INSTRUCTIONS.md"

PSHELL="$(command -v pwsh || command -v powershell || true)"
if [ -n "$PSHELL" ]; then
  for modus in neutral codex claude; do
    BASH_ZIEL="$WURZEL/paritaet-bash-$modus"; PS_ZIEL="$WURZEL/paritaet-ps-$modus"; mkdir -p "$BASH_ZIEL" "$PS_ZIEL"
    [ "$modus" != codex ] || { printf '# Eigene Regeln\n' > "$BASH_ZIEL/AGENTS.md"; cp "$BASH_ZIEL/AGENTS.md" "$PS_ZIEL/AGENTS.md"; }
    ausfuehren "$BASH_ZIEL" "$modus"
    PS_ARG="$PS_ZIEL"; command -v cygpath >/dev/null 2>&1 && PS_ARG="$(cygpath -w "$PS_ZIEL")"
    "$PSHELL" -NoProfile -ExecutionPolicy Bypass -File "$QUELLE/install.ps1" "$PS_ARG" "$modus" > "$PS_ZIEL.log" 2>&1 || fehler "PowerShell-Installation ($modus) schlug fehl"
    diff -r --exclude='*.log' "$BASH_ZIEL" "$PS_ZIEL" > "$WURZEL/$modus.diff" 2>&1 || { fehler "Bash/PowerShell unterscheiden sich ($modus)"; head -20 "$WURZEL/$modus.diff"; }
  done
else echo '== Hinweis: pwsh/PowerShell nicht gefunden — PowerShell-Paritaet uebersprungen'; fi
if [ "$FEHLER" -ne 0 ]; then exit 1; fi
echo '== Alle Installer-Tests erfolgreich'
