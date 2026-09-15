# scratchpad

Arbeitsanleitungen fuer KI-gestuetzte Programmieraufgaben.

## Voraussetzungen

| Programm | Noetig fuer |
|---|---|
| Git | `/ref` und das Zielprojekt |
| Node.js 22 oder neuer (mit `npm`) | Die Uebungs-App bauen und testen |
| Python 3 | Installer im Modus `claude` |
| Claude Code oder Codex CLI | Der Agent |

## Installation

```text
powershell -ExecutionPolicy Bypass -File C:\source\scratchpad\install.ps1 C:\projekte\mein-projekt <modus>
bash /c/source/scratchpad/install.sh ~/projekte/mein-projekt <modus>
```

| Modus | Installierte Inhalte |
|---|---|
| `neutral` | Anleitungen unter `.agents/`. |
| `codex` | Neutraler Kern, Skills unter `.agents/skills/` und ein Scratchpad-Block in `AGENTS.md`. |
| `claude` | Claude-Commands, Skills, Hooks und Einstellungen unter `.claude/`. |

Ohne `<modus>` fragt der Installer nach der Auswahl. Pro Zielprojekt wird ein Modus installiert.

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

## Installer-Tests

```text
bash test_install.sh
```
