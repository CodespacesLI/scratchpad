#!/usr/bin/env bash
# Prueft und installiert die Voraussetzungen fuer scratchpad unter macOS und Linux.
# Aufruf: bash setup.sh [claude|codex|beide|pruefen]
#
# Installiert fehlende Basis-Werkzeuge (Git, Node.js 22+, Python 3) ueber brew, apt oder
# dnf und den gewaehlten Agenten ueber dessen offiziellen Weg. "pruefen" installiert
# nichts. Bewusst Bash-3.2-kompatibel (macOS-Standard): kein ${var,,}, keine
# assoziativen Arrays.
set -u

MIN_NODE=22
AUSWAHL="${1:-}"
if [ -z "$AUSWAHL" ]; then
  printf 'Agent installieren (claude, codex, beide) oder nur pruefen (pruefen): '
  IFS= read -r AUSWAHL || AUSWAHL=""
fi
AUSWAHL="$(printf '%s' "$AUSWAHL" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')"
case "$AUSWAHL" in
  claude|codex|beide|pruefen) ;;
  *) echo "FEHLER: Unbekannte Auswahl: $AUSWAHL (erlaubt: claude, codex, beide, pruefen)" >&2; exit 1 ;;
esac

PATH_VORHER="$PATH"
export PATH="$HOME/.local/bin:$PATH"
INSTALLIERT=0

als_root() { if [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1; then sudo "$@"; else "$@"; fi; }
gewaehlt() { [ "$AUSWAHL" = beide ] || [ "$AUSWAHL" = "$1" ]; }

git_version() { git --version 2>/dev/null | awk '{print $3}'; }
node_version() {
  command -v node >/dev/null 2>&1 || return 1
  v="$(node -p 'process.versions.node' 2>/dev/null)" || return 1
  [ "${v%%.*}" -ge "$MIN_NODE" ] 2>/dev/null || return 1
  echo "v$v"
}
npm_version() { npm --version 2>/dev/null; }
python_version() {
  for p in python3 python; do
    if "$p" -c 'import sys; assert sys.version_info >= (3, 9)' >/dev/null 2>&1; then
      "$p" -c 'import sys; print(sys.version.split()[0])'; return 0
    fi
  done
  return 1
}
agent_version() { "$1" --version 2>/dev/null | head -n 1; }

installiere_basis() {
  case "$(uname -s)" in
    Darwin)
      if ! command -v brew >/dev/null 2>&1; then
        echo "Installiere Homebrew (fragt nach dem Passwort) ..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do
          if [ -x "$b" ]; then eval "$("$b" shellenv)"; break; fi
        done
      fi
      if command -v brew >/dev/null 2>&1; then
        [ -n "$(git_version)" ] || brew install git
        node_version >/dev/null || brew install node
        python_version >/dev/null || brew install python
      fi
      ;;
    Linux)
      if command -v apt-get >/dev/null 2>&1; then
        pakete=""
        [ -n "$(git_version)" ] || pakete="$pakete git"
        python_version >/dev/null || pakete="$pakete python3"
        command -v curl >/dev/null 2>&1 || pakete="$pakete curl ca-certificates"
        if [ -n "$pakete" ]; then
          # shellcheck disable=SC2086 # $pakete ist eine Wortliste
          als_root apt-get update && als_root apt-get install -y $pakete
        fi
        if ! node_version >/dev/null; then
          curl -fsSL "https://deb.nodesource.com/setup_${MIN_NODE}.x" | als_root bash - \
            && als_root apt-get install -y nodejs
        fi
      elif command -v dnf >/dev/null 2>&1; then
        [ -n "$(git_version)" ] || als_root dnf install -y git
        python_version >/dev/null || als_root dnf install -y python3
        if ! node_version >/dev/null; then
          curl -fsSL "https://rpm.nodesource.com/setup_${MIN_NODE}.x" | als_root bash - \
            && als_root dnf install -y nodejs
        fi
      else
        echo "WARNUNG: Paketmanager nicht erkannt. Git, Node.js ${MIN_NODE}+ und Python 3 von Hand installieren." >&2
      fi
      ;;
    *)
      echo "WARNUNG: Unbekanntes System $(uname -s). Unter Windows setup.cmd verwenden." >&2
      ;;
  esac
}

installiere_codex() {
  # Ist das globale npm-Verzeichnis nicht beschreibbar (z.B. /usr bei NodeSource),
  # landet Codex in ~/.local — dort liegt auch claude, ohne sudo.
  prefix="$(npm prefix -g 2>/dev/null)"
  if [ -n "$prefix" ] && { [ -w "$prefix/lib/node_modules" ] || [ -w "$prefix/bin" ]; }; then
    npm install -g @openai/codex
  else
    npm install -g --prefix "$HOME/.local" @openai/codex
  fi
}

if [ "$AUSWAHL" != pruefen ]; then
  if [ -z "$(git_version)" ] || ! node_version >/dev/null || [ -z "$(npm_version)" ] || ! python_version >/dev/null; then
    installiere_basis
    INSTALLIERT=1
  fi
  if gewaehlt claude && [ -z "$(agent_version claude)" ]; then
    echo "Installiere Claude Code (offizieller Installer) ..."
    curl -fsSL https://claude.ai/install.sh | bash
    INSTALLIERT=1
  fi
  if gewaehlt codex && [ -z "$(agent_version codex)" ]; then
    if [ -n "$(npm_version)" ]; then
      echo "Installiere Codex CLI ueber npm ..."
      installiere_codex
      INSTALLIERT=1
    else
      echo "WARNUNG: npm fehlt, Codex CLI nicht installiert." >&2
    fi
  fi
fi

FEHLT=0
zeile() { # zeile <status> <name> <wert>
  case "$1" in
    ok) printf '  [ok]    %-12s %s\n' "$2" "$3" ;;
    fehlt) printf '  [fehlt] %s\n' "$2"; FEHLT=1 ;;
    *) printf '  [-]     %-12s nicht installiert\n' "$2" ;;
  esac
}
pflicht() { if [ -n "$2" ]; then zeile ok "$1" "$2"; else zeile fehlt "$1" ""; fi; }

echo
echo "Stand:"
pflicht "Git" "$(git_version)"
pflicht "Node.js ${MIN_NODE}+" "$(node_version)"
pflicht "npm" "$(npm_version)"
pflicht "Python 3.9+" "$(python_version)"
AGENT_DA=0
for agent in claude codex; do
  v="$(agent_version "$agent")"
  if [ -n "$v" ]; then zeile ok "$agent" "$v"; AGENT_DA=1
  elif gewaehlt "$agent"; then zeile fehlt "$agent" ""
  else zeile optional "$agent" ""; fi
done
if [ "$AUSWAHL" = pruefen ] && [ "$AGENT_DA" -eq 0 ]; then
  echo "  Kein Agent gefunden: bash setup.sh claude oder bash setup.sh codex"
  FEHLT=1
fi

echo
if [ "$FEHLT" -ne 0 ]; then
  if [ "$AUSWAHL" = pruefen ]; then
    echo "Es fehlt noch etwas (siehe oben). Installieren mit: bash setup.sh claude   (oder: codex, beide)"
  else
    echo "Es fehlt noch etwas (siehe oben). Ohne lokale Installation geht es mit dem Dev Container (README)."
  fi
  exit 1
fi
echo "Alles bereit. Weiter: python3 start.py claude   (oder: python3 start.py codex)"
case ":$PATH_VORHER:" in
  *":$HOME/.local/bin:"*) ;;
  *) if [ -d "$HOME/.local/bin" ]; then
       echo "Wichtig: \$HOME/.local/bin in den PATH aufnehmen, z.B.:"
       echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc   (bash: ~/.bashrc)"
     fi ;;
esac
if [ "$INSTALLIERT" -eq 1 ]; then echo "Danach ein NEUES Terminal oeffnen."; fi
exit 0
