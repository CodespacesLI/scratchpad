# scratchpad

Arbeitsanleitungen fuer KI-gestuetzte Programmieraufgaben, mit einer fertigen Uebung
(Task-Board) fuer Claude Code und Codex.

## Schnellstart

Es gibt drei Wege. Alle enden am selben Punkt: ein Terminal, in dem ein Befehl das
Uebungsprojekt anlegt.

| Weg | Du brauchst | Geeignet, wenn |
|---|---|---|
| **A: Eigener Rechner** | Nichts, `setup` installiert den Rest. Unter Windows ohne Admin-Rechte. | Du Programme in deinem Benutzerordner starten darfst |
| **B: Dev Container** | Docker und VS Code (oder Cursor, JetBrains). Docker zu installieren braucht Admin-Rechte. | Docker schon da ist und du lokal nichts sonst installieren willst |
| **C: GitHub Codespaces** | Nur einen Browser und ein GitHub-Konto | Auf deinem Rechner gar nichts geht, z.B. Firmenrechner mit gesperrten Programmen |

### Weg A: Eigener Rechner

**1. Repo holen:** `git clone https://github.com/CodespacesLI/scratchpad.git` oder auf
GitHub „Code“ → „Download ZIP“ und entpacken.

**2. Voraussetzungen installieren.** Im Ordner `scratchpad`:

| System | Befehl |
|---|---|
| Windows | `.\setup.cmd claude` |
| macOS oder Linux | `bash setup.sh claude` |

Statt `claude` geht auch `codex` oder `beide`. Mit `pruefen` wird nur geprueft und nichts
installiert. Am Ende steht „Alles bereit“ oder eine Liste, was fehlt. Danach **ein neues
Terminal oeffnen**, damit die neuen Programme gefunden werden.

**3. Uebungsprojekt anlegen und Agent starten:**

| System | Befehle |
|---|---|
| Windows | `python start.py claude`, dann `cd task-board`, dann `claude` |
| macOS oder Linux | `python3 start.py claude`, dann `cd task-board`, dann `claude` |

### Weg B: Dev Container (Docker)

Voraussetzung: [Docker Desktop](https://www.docker.com/products/docker-desktop/) und VS
Code mit der Erweiterung „Dev Containers“.

1. Den Ordner `scratchpad` in VS Code oeffnen und „Reopen in Container“ waehlen (oder F1 →
   „Dev Containers: Reopen in Container“). Der erste Start baut das Image und dauert
   einige Minuten.
2. Im Terminal von VS Code: `python start.py claude`, dann `cd task-board`, dann `claude`.
3. Beim ersten Start einmal anmelden. Der Login bleibt auch nach einem Neubau des
   Containers erhalten.

Im Container sind Node.js 22, Git, Python, Claude Code, Codex und die Systempakete fuer
Playwright vorinstalliert. `npm run dev` wird automatisch weitergeleitet und ist unter
<http://localhost:5173> erreichbar.

**Tipp fuer Windows:** `npm install` ist in einem eingebundenen Windows-Ordner langsam.
Schneller geht es mit F1 → „Dev Containers: Clone Repository in Container Volume“ und der
Repo-Adresse.

### Weg C: GitHub Codespaces

Auf der GitHub-Seite des Repos: „Code“ → „Codespaces“ → „Create codespace“. Das startet
denselben Container wie Weg B im Browser. Weiter wie bei Weg B ab Schritt 2. Die Adresse
der laufenden App steht im Reiter „Ports“.

## Voraussetzungen im Detail

`setup` installiert alles, was fehlt. Diese Tabelle ist nur fuer den Fall, dass du von
Hand installierst.

| Programm | Noetig fuer | `setup` installiert ueber |
|---|---|---|
| Git | `/ref` und das Projekt. Unter Windows bringt es die Git Bash mit, die Claude Code braucht. | winget (pro Benutzer), brew, apt oder dnf |
| Node.js 22 oder neuer (mit `npm`) | Die Uebungs-App bauen und testen | ZIP von nodejs.org nach `%LOCALAPPDATA%\Programs\nodejs` (Windows), brew, NodeSource |
| Python 3.9 oder neuer | Installer und die Hooks im Modus `claude` | winget (pro Benutzer), brew, apt oder dnf |
| Claude Code oder Codex CLI | Der Agent | offizieller Installer (Claude), npm (Codex) |

Unter Windows braucht `setup` keine Admin-Rechte: alles landet im Benutzerordner und im
Benutzer-PATH. Unter macOS und Linux fragen brew, apt und dnf nach dem Passwort.

Unter Windows heisst der Befehl `python`, unter macOS und Linux `python3`. Oeffnet
`python` unter Windows den Microsoft Store, ist Python nicht wirklich installiert. `setup`
erkennt das.

## In ein eigenes Projekt installieren

`start.py` ist die Abkuerzung fuer die Uebung. Fuer jedes andere Projekt:

```text
python install.py <pfad-zum-projekt> [neutral|codex|claude]
```

| Modus | Installierte Inhalte |
|---|---|
| `neutral` | Anleitungen unter `.agents/`. |
| `codex` | Neutraler Kern, Skills unter `.agents/skills/` und ein Scratchpad-Block in `AGENTS.md`. |
| `claude` | Claude-Commands, Skills, Hooks und Einstellungen unter `.claude/`. |

Ohne Modus fragt der Installer nach der Auswahl. Pro Zielprojekt wird ein Modus
installiert. Ein zweiter Lauf aktualisiert die Dateien, ohne etwas doppelt einzutragen.

## Wichtige Pfade

| Pfad | Zweck |
|---|---|
| `.agents/vorgehen/` oder `.claude/vorgehen/` | Anleitungen fuer Brainstorm, Plan und Bau. |
| `.agents/tasks/` oder `.claude/tasks/` | Plan-Dateien. |
| `.agents/state/` oder `.claude/state/` | Handoff-Brief und Stand einer manuellen Review-Schleife. |
| `.agents/references/` oder `.claude/references/` | `referenzen.md` (feste Quellenliste), nach `/ref` auch `INDEX.md` und `sources/` (Git-Klone, per `.gitignore` ausgeschlossen). |
| `.agents/INSTRUCTIONS.md` | Toolneutrale Regeln. |
| `AGENTS.md` | Codex erhaelt hier den Scratchpad-Block. |
| `.claude/commands/` und `.claude/hooks/` | Nur Claude: Commands und automatische Pruefungen. |

## Arbeitsbefehle

Die Befehle werden in der Claude-Version direkt eingegeben. In der Codex-Version wird
die Nachricht mit dem angegebenen Wort begonnen.

| Befehl | Zweck |
|---|---|
| `/brainstorm` / `Brainstorm:` | Anforderungen klaeren und einen kurzen Brief bestaetigen. |
| `/ref <slug>` / `Referenzen: <slug>` | Beim Planen oder Bauen: fertigen Code fuer ein konkretes Problem aus der festen Liste per Git holen. `references/INDEX.md` sagt danach, welche Datei die Vorlage wofuer ist. |
| `/plan` / `Plane:` | Aus dem Brief einen testbaren Plan mit kleinen Aufgaben erstellen, jede Aufgabe mit Vorlage aus dem Index. |
| `/build` / `Baue:` | Die offenen Aufgaben aus dem Plan umsetzen und testen. |
| `/handoff` | Arbeitsstand in einer Datei fuer ein neues Gespraech festhalten. |
| `/clear` | Das aktuelle Gespraech manuell leeren. Nur Claude verwendet diesen Schritt als eigenen Command. |
| `/resume` | Den Handoff-Brief lesen und den Arbeitsstand gegen die Dateien pruefen. |
| `/loop` | Optional: Kriterien pruefen, konkrete Maengel beheben und den Stand der Runde dokumentieren. |

`/handoff`, `/clear`, `/resume` und `/loop` sind in der Claude-Version als Commands
vorhanden. In der Codex-Version werden dieselben Aufgaben als normale Nachrichten an den
Agenten gestellt; die Arbeitsblaetter beschreiben den jeweiligen Ablauf.

## Uebung

| Datei | Verwendung |
|---|---|
| [uebung/aufgabe-claude.md](uebung/aufgabe-claude.md) | Arbeitsblatt fuer den Claude-Modus. |
| [uebung/aufgabe-codex.md](uebung/aufgabe-codex.md) | Arbeitsblatt fuer den Codex-Modus. |
| [uebung/referenzen.md](uebung/referenzen.md) | Fertige Quellenliste mit Repository, Branch, Lizenz, Pfaden und Vorlage pro Datei. Der Installer kopiert sie nach `references/referenzen.md`, `/ref` holt die Dateien. |
| [uebung/loesungsblatt.md](uebung/loesungsblatt.md) | Erwartete fachliche Entscheidungen und moegliche Planstruktur. |

Die fachliche Uebung ist in beiden Modi gleich. Die Arbeitsblaetter unterscheiden sich nur in Commands, Pfaden und dem manuellen Uebergang zwischen Gesprächen.

Quality Gate mit Playwright ist optional. Es wird nur nach dem Bau ausgefuehrt, wenn Zeit vorhanden ist.

## Tests

```text
python test_install.py
python test_treiber.py
python hooks/test_guard_tdd.py        (ebenso die anderen hooks/test_*.py)
```

GitHub Actions fuehrt alle Tests unter Windows, macOS und Linux aus, dazu `setup` auf allen
drei Systemen und den Bau des Dev Containers (`.github/workflows/tests.yml`).
