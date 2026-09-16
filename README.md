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
GitHub „Code“ → „Download ZIP“ und entpacken. Beim ZIP heisst der Ordner `scratchpad-main`
und liegt nach dem Entpacken oft doppelt ineinander. Gemeint ist immer der Ordner, in dem
`setup.cmd` liegt.

**2. Terminal im Ordner `scratchpad` oeffnen.** Alle weiteren Befehle tippst du dort ein.

| System | So geht es |
|---|---|
| Windows | Den Ordner `scratchpad` im Explorer oeffnen, oben in die Adresszeile klicken, `powershell` eintippen und Enter druecken |
| macOS | Programm „Terminal“ starten (Cmd+Leertaste, „Terminal“), `cd ` tippen (mit Leerzeichen), den Ordner `scratchpad` ins Fenster ziehen und Enter druecken |
| Linux | Rechtsklick auf den Ordner `scratchpad` und „Im Terminal oeffnen“ |

**3. Pruefen, was fehlt.** Dieser Befehl installiert nichts, er zeigt nur den Stand:

| Befehl | Wann |
|---|---|
| `.\setup.cmd pruefen` | Windows |
| `bash setup.sh pruefen` | macOS oder Linux |

Jede Zeile mit `[ok]` ist schon da, jede mit `[fehlt]` noch nicht. Steht am Ende „Alles
bereit“, geht es direkt mit Schritt 5 weiter. Sonst mit Schritt 4.

**4. Installieren, was fehlt.** Nimm genau **einen** Befehl, passend zu deinem System und
deinem Agenten. Er installiert alles, was in Schritt 3 gefehlt hat, also Git, Node.js, npm,
Python und den Agenten, und laesst vorhandene Programme in Ruhe:

| Befehl | Wann |
|---|---|
| `.\setup.cmd claude` | Windows, du arbeitest mit Claude Code |
| `.\setup.cmd codex` | Windows, du arbeitest mit Codex |
| `.\setup.cmd beide` | Windows, du willst Claude Code und Codex |
| `bash setup.sh claude` | macOS oder Linux, du arbeitest mit Claude Code |
| `bash setup.sh codex` | macOS oder Linux, du arbeitest mit Codex |
| `bash setup.sh beide` | macOS oder Linux, du willst Claude Code und Codex |

Danach das Terminal **schliessen und wie in Schritt 2 neu oeffnen**, damit die neuen
Programme gefunden werden. Dann Schritt 3 nochmal ausfuehren. Steht dort immer noch
`[fehlt]`, lies die gelben `WARNUNG`-Zeilen der Installation. Kommst du damit nicht weiter,
nimm Weg C (Codespaces), der braucht auf deinem Rechner nichts.

**5. Uebungsprojekt anlegen und Agent starten.** Die drei Befehle nacheinander eintippen,
jeweils mit Enter:

| Befehle | Wann |
|---|---|
| `python start.py claude`<br>`cd task-board`<br>`claude` | Windows, du arbeitest mit Claude Code |
| `python start.py codex`<br>`cd task-board`<br>`codex` | Windows, du arbeitest mit Codex |
| `python3 start.py claude`<br>`cd task-board`<br>`claude` | macOS oder Linux, du arbeitest mit Claude Code |
| `python3 start.py codex`<br>`cd task-board`<br>`codex` | macOS oder Linux, du arbeitest mit Codex |

### Weg B: Dev Container (Docker)

Voraussetzung: [Docker Desktop](https://www.docker.com/products/docker-desktop/) und VS
Code mit der Erweiterung „Dev Containers“.

1. Windows: F1 → „Dev Containers: Clone Repository in Container Volume“ waehlen und
   `https://github.com/CodespacesLI/scratchpad.git` eingeben. Das Repo liegt dann direkt
   im Container, dadurch laeuft `npm install` viel schneller als in einem Windows-Ordner.
   Mac und Linux: das Repo wie in Weg A Schritt 1 holen, den Ordner `scratchpad` in VS Code
   oeffnen und „Reopen in Container“ waehlen (oder F1 → „Dev Containers: Reopen in Container“).
   Der erste Start baut das Image und dauert einige Minuten.
2. Im Terminal von VS Code: `python start.py claude`, dann `cd task-board`, dann `claude`.
3. Beim ersten Start einmal anmelden. Der Login bleibt auch nach einem Neubau des
   Containers erhalten.

Im Container sind Node.js 22, Git, Python, Claude Code, Codex und die Systempakete fuer
Playwright vorinstalliert. `npm run dev` wird automatisch weitergeleitet und ist unter
<http://localhost:5173> erreichbar.

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
| Node.js 22 oder neuer (mit `npm`) | Die Uebungs-App bauen und testen, die Statuszeile im Modus `claude` | ZIP von nodejs.org nach `%LOCALAPPDATA%\Programs\nodejs` (Windows), brew, NodeSource |
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
| `.claude/statuszeile.js` | Nur Claude: Statuszeile unter der Eingabe mit Modell, Git-Branch, belegtem Kontext (Tokens und Prozent vom Fenster) und bisherigen Kosten. Eine eigene `statusLine` des Projekts bleibt. |

## Arbeitsbefehle

Die Befehle werden in der Claude-Version direkt eingegeben. In der Codex-Version wird
die Nachricht mit dem angegebenen Wort begonnen.

| Befehl | Zweck |
|---|---|
| `/brainstorm` / `Brainstorm:` | Anforderungen klaeren, Vorlagen fuer die schwierigen Teile waehlen und einen kurzen Brief bestaetigen. |
| `/ref <slug>` / `Referenzen: <slug>` | Nach dem Brainstorm, vor dem Plan: fertigen Code fuer die im Brief gewaehlten Slugs aus der festen Liste per Git holen. `references/INDEX.md` sagt danach, welche Datei die Vorlage wofuer ist. |
| `/plan` / `Plane:` | Aus dem Brief einen testbaren Plan mit kleinen Aufgaben erstellen, passende Aufgaben mit Vorlage aus dem Index. |
| `/build` / `Baue:` | Alle offenen Aufgaben aus dem Plan am Stueck umsetzen und testen. Angehalten wird nur bei einer echten Blockade oder wenn der Kontext voll ist; ein erneuter Aufruf macht beim ersten offenen Task weiter. |
| `/handoff` | Arbeitsstand in einer Datei fuer ein neues Gespraech festhalten. |
| `/clear` | Das aktuelle Gespraech manuell leeren. Nur Claude verwendet diesen Schritt als eigenen Command. |
| `/resume` | Den Handoff-Brief lesen, den Arbeitsstand gegen die Dateien pruefen und die naechste offene Aufgabe nennen. Stand der Vorgaenger im Bau, geht es danach mit `/build` weiter. |
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
| [uebung/loesungsblatt.md](uebung/loesungsblatt.md) | Musterloesung fuer die Kursleitung: vollstaendige Beispiel-Nachrichten fuer beide Modi, erwartete fachliche Entscheidungen, moegliche Planstruktur und Vorlagen. |

Die fachliche Uebung ist in beiden Modi gleich. Die Arbeitsblaetter unterscheiden sich nur in Commands, Pfaden und dem manuellen Uebergang zwischen Gesprächen, falls der Kontext beim Bauen voll wird.

Quality Gate mit Playwright ist optional. Es wird nur nach dem Bau ausgefuehrt, wenn Zeit vorhanden ist.

## Tests

```text
python test_install.py
python test_treiber.py
python hooks/test_guard_tdd.py        (ebenso die anderen hooks/test_*.py)
```
