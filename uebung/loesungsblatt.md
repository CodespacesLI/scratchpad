# Loesungsblatt: Task-Board

Dieses Blatt beschreibt eine erwartete Loesung. Andere Loesungen sind gueltig, wenn sie den Abnahmekriterien entsprechen und begruendet sind.

## Beispiel-Nachrichten

Musterloesung fuer die Kursleitung. So koennte ein kompletter Durchlauf aussehen, Nachricht
fuer Nachricht in der Reihenfolge, in der sie abgeschickt werden. Die Teilnehmenden
formulieren ihre Nachrichten selbst. Eine eigene Formulierung ist richtig, wenn die Inhalte
aus der Liste „Deine Nachricht enthaelt:“ im Arbeitsblatt drin sind.

Welche Vorlagen genutzt werden, entscheiden die Teilnehmenden schon in Schritt 1 beim
Klaeren der Anforderungen: Sie waehlen fuer jeden schwierigen Teil den Slug aus der Tabelle
„Vorlagen“, und der Brief nennt jeden Slug mit dem Problem, das er loest. In Schritt 2 holen
sie genau diese Slugs, jeden genau einmal, vor dem Plan. Beim Bauen wird nichts mehr geholt,
der Agent kopiert aus dem Feld „Vorlage:“ der Aufgaben. Nur `playwright` holen sie spaeter,
im optionalen Schritt 6.

### Claude

#### Schritt 0: Vorbereiten

Im Terminal im Ordner `scratchpad`, nach dem Setup:

```text
python start.py claude
cd task-board
claude
```

#### Schritt 1: Anforderungen klaeren

```text
/brainstorm Ein Task-Board fuer eine Person, nur im Browser. Drei Spalten: Offen, In Arbeit, Fertig. Eine Karte hat einen Titel, eine optionale Beschreibung und eine Prioritaet. Karten lassen sich mit der Maus und mit der Tastatur in eine andere Spalte verschieben. Ein Klick auf eine Karte oeffnet einen Dialog zum Bearbeiten. Filter nach Prioritaet und nach einem Wort im Titel. Nach dem Neuladen der Seite ist alles noch da. Eine leere Spalte zeigt einen Hinweis. Kaputte gespeicherte Daten zeigen eine Meldung. Nicht bauen: Login, Server, Synchronisation, eigene Spalten, Anhaenge, Kommentare, Termine, Sortieren innerhalb einer Spalte, Farbthemen, Handy-Ansicht, Veroeffentlichen. Frag mich ausserdem zu diesen drei Punkten: Was passiert, wenn eine Spalte sehr viele Karten hat? Was passiert, wenn ein Filter aktiv ist und ich eine Karte verschiebe? Was passiert, wenn die App in zwei Browserfenstern gleichzeitig offen ist?
```

Nach Claudes erster Fragerunde kommt diese Antwort. Sie enthaelt die drei Entscheidungen
aus der Tabelle „Entscheidungen aus dem Brainstorm“ und geht auch dann raus, wenn Claude
nicht nach den drei Punkten gefragt hat:

```text
Zu den drei Punkten: Ab 20 Karten zeigt eine Spalte eine sichtbare Warnung. Verschieben in diese Spalte bleibt trotzdem moeglich. Der Filter aendert nur die Ansicht. Verschiebe ich bei aktivem Filter eine Karte, aendert sich ihre echte Spalte, und ausgeblendete Karten behalten ihre Reihenfolge. Zwei Browserfenster synchronisieren sich nicht live. Beim naechsten Neuladen gilt der zuletzt gespeicherte Stand.
```

Wenn Claude fragt, ob es fuer die schwierigen Teile schon fertigen Code gibt, kommt diese
Antwort. Sie geht auch dann raus, wenn Claude nicht danach gefragt hat:

```text
Fuer die schwierigen Teile nutzen wir fertigen Code aus der Vorlagen-Liste: zustand fuer das Speichern im Browser und das Abfangen kaputter gespeicherter Daten. vitest fuer die Einrichtung der Unit-Tests. testing-library fuer Tests, die Dialog, Knoepfe und Felder ueber Rolle und Namen finden. dnd-kit fuer das Verschieben der Karten mit Maus und Tastatur zwischen den Spalten. shadcn fuer den Dialog, das Auswahlfeld fuer die Prioritaet und die Eingabefelder. Automatische Browser-Tests mit playwright nehmen wir jetzt nicht dazu.
```

Wenn Claude den Brief zeigt und die drei Entscheidungen sowie die fuenf Slugs mit ihrem
Problem darin stehen:

```text
Der Brief passt so.
```

#### Schritt 2: Vorlagen holen

Die fuenf Slugs aus dem Brief, in einem Befehl:

```text
/ref zustand vitest testing-library dnd-kit shadcn
```

Danach pruefen: In der Antwort steht kein `FEHLT`, und `.claude/references/INDEX.md` nennt
alle fuenf Slugs.

#### Schritt 3: Plan erstellen

Wenn `.claude/references/INDEX.md` alle fuenf Slugs nennt:

```text
/plan Nimm den Brief aus Schritt 1 in diesem Chat und speichere den Plan als board.md. Schau zuerst in .claude/references/INDEX.md nach, wo es fertigen Code fuer die schwierigen Teile gibt, und trag bei jeder passenden Aufgabe die Vorlage mit dem lokalen Pfad ein.
```

Wenn `.claude/tasks/board.md` alle drei Pruefpunkte aus dem Arbeitsblatt erfuellt:

```text
Der Plan ist freigegeben.
```

#### Schritt 4: Bauen

Wenn der Plan freigegeben ist:

```text
/build .claude/tasks/board.md Baue alle offenen Aufgaben dieses Plans am Stueck, ohne zwischendurch anzuhalten. Halte nur an, wenn der Plan eine Frage nicht beantwortet und du sonst falsch bauen wuerdest, oder wenn der Kontext voll ist.
```

Nur wenn der Waechter sich meldet und Claude sagt, dass der Zyklus dran ist (bei rund 120 000 Tokens; ab etwa 100 000 wird Claude spuerbar
ungenauer, der Rest ist Spielraum), vier Befehle nacheinander, jeder erst, wenn Claude mit dem vorigen fertig ist:

```text
/handoff
```

```text
/clear
```

```text
/resume
```

```text
/build .claude/tasks/board.md
```

Wenn Claude meldet, dass alle Aufgaben fertig sind, im zweiten Terminal im Ordner
`task-board`, nacheinander:

```text
npm test
npm run dev
```

Danach im Browser drei Spalten, Karte anlegen, Neuladen, Verschieben und Filter pruefen und
in `.claude/tasks/done/board.md` nachsehen, dass jede Aufgabe abgehakt oder begruendet
durchgestrichen ist. Claude hat den fertigen Plan dorthin verschoben.

#### Schritt 5: Abnahme

Wenn Abnahmepunkt 5 im Browser nicht funktioniert:

```text
Abnahmepunkt 5 geht nicht. Ich waehle mit Tab eine Karte in der Spalte Offen und nehme sie mit der Leertaste auf. Dann druecke ich die Pfeiltaste nach rechts, aber die Karte bleibt in Offen. Schreib zuerst einen Test, der diesen Fehler zeigt, und behebe ihn erst danach.
```

#### Schritt 6: Optional: automatische Browser-Tests

```text
/ref playwright
```

Wenn in der Antwort kein `FEHLT` steht:

```text
Schreibe Playwright-Tests fuer diese sechs Punkte und fuehre sie aus. Nutze dafuer die Playwright-Vorlage aus .claude/references/INDEX.md. Behebe gefundene Fehler, aber baue keine neuen Funktionen.
1. Beim Tippen im Dialog bleibt der Cursor im richtigen Feld.
2. Jede Karte zeigt im Dialog ihre eigenen Werte, auch nach dem Wechsel zu einer anderen Karte.
3. Verschieben geht mit Tab, Leertaste und Pfeiltasten. Ein unsichtbarer Text fuer Screenreader meldet jeden Schritt.
4. Alle Knoepfe, Felder und der Dialog haben einen Namen fuer Screenreader.
5. Der Fokus bleibt im offenen Dialog und springt beim Schliessen zurueck zur Karte.
6. Beim Anlegen, Verschieben, Bearbeiten und Filtern erscheinen keine Fehler in der Browser-Konsole.
```

### Codex

#### Schritt 0: Vorbereiten

Im Terminal im Ordner `scratchpad`, nach dem Setup:

```text
python start.py codex
cd task-board
codex
```

#### Schritt 1: Anforderungen klaeren

```text
Brainstorm: Ein Task-Board fuer eine Person, nur im Browser. Drei Spalten: Offen, In Arbeit, Fertig. Eine Karte hat einen Titel, eine optionale Beschreibung und eine Prioritaet. Karten lassen sich mit der Maus und mit der Tastatur in eine andere Spalte verschieben. Ein Klick auf eine Karte oeffnet einen Dialog zum Bearbeiten. Filter nach Prioritaet und nach einem Wort im Titel. Nach dem Neuladen der Seite ist alles noch da. Eine leere Spalte zeigt einen Hinweis. Kaputte gespeicherte Daten zeigen eine Meldung. Nicht bauen: Login, Server, Synchronisation, eigene Spalten, Anhaenge, Kommentare, Termine, Sortieren innerhalb einer Spalte, Farbthemen, Handy-Ansicht, Veroeffentlichen. Frag mich ausserdem zu diesen drei Punkten: Was passiert, wenn eine Spalte sehr viele Karten hat? Was passiert, wenn ein Filter aktiv ist und ich eine Karte verschiebe? Was passiert, wenn die App in zwei Browserfenstern gleichzeitig offen ist?
```

Nach der ersten Fragerunde von Codex kommt diese Antwort. Sie geht auch dann raus, wenn
Codex nicht nach den drei Punkten gefragt hat:

```text
Zu den drei Punkten: Ab 20 Karten zeigt eine Spalte eine sichtbare Warnung. Verschieben in diese Spalte bleibt trotzdem moeglich. Der Filter aendert nur die Ansicht. Verschiebe ich bei aktivem Filter eine Karte, aendert sich ihre echte Spalte, und ausgeblendete Karten behalten ihre Reihenfolge. Zwei Browserfenster synchronisieren sich nicht live. Beim naechsten Neuladen gilt der zuletzt gespeicherte Stand.
```

Wenn Codex fragt, ob es fuer die schwierigen Teile schon fertigen Code gibt, kommt diese
Antwort. Sie geht auch dann raus, wenn Codex nicht danach gefragt hat:

```text
Fuer die schwierigen Teile nutzen wir fertigen Code aus der Vorlagen-Liste: zustand fuer das Speichern im Browser und das Abfangen kaputter gespeicherter Daten. vitest fuer die Einrichtung der Unit-Tests. testing-library fuer Tests, die Dialog, Knoepfe und Felder ueber Rolle und Namen finden. dnd-kit fuer das Verschieben der Karten mit Maus und Tastatur zwischen den Spalten. shadcn fuer den Dialog, das Auswahlfeld fuer die Prioritaet und die Eingabefelder. Automatische Browser-Tests mit playwright nehmen wir jetzt nicht dazu.
```

Wenn Codex den Brief zeigt und die drei Entscheidungen sowie die fuenf Slugs mit ihrem
Problem darin stehen:

```text
Der Brief passt so.
```

#### Schritt 2: Vorlagen holen

Die fuenf Slugs aus dem Brief, in einer Nachricht:

```text
Referenzen: zustand vitest testing-library dnd-kit shadcn
```

Danach pruefen: In der Antwort steht kein `FEHLT`, und `.agents/references/INDEX.md` nennt
alle fuenf Slugs.

#### Schritt 3: Plan erstellen

Wenn `.agents/references/INDEX.md` alle fuenf Slugs nennt:

```text
Plane: Nimm den Brief aus Schritt 1 in diesem Chat und speichere den Plan als board.md. Schau zuerst in .agents/references/INDEX.md nach, wo es fertigen Code fuer die schwierigen Teile gibt, und trag bei jeder passenden Aufgabe die Vorlage mit dem lokalen Pfad ein.
```

Wenn `.agents/tasks/board.md` alle drei Pruefpunkte aus dem Arbeitsblatt erfuellt:

```text
Der Plan ist freigegeben.
```

#### Schritt 4: Bauen

Wenn der Plan freigegeben ist:

```text
Baue: den Plan .agents/tasks/board.md. Baue alle offenen Aufgaben dieses Plans, eine nach der anderen, ohne zwischendurch anzuhalten. Halte nur an, wenn der Plan eine Frage nicht beantwortet und du sonst falsch bauen wuerdest.
```

Nur wenn der Chat rund 120 000 Tokens erreicht (ab etwa 100 000 wird Codex spuerbar
ungenauer, der Rest ist Spielraum), nacheinander, jeder
Schritt erst, wenn Codex mit dem vorigen fertig ist:

```text
Schreibe den aktuellen Stand in die Datei .agents/state/handoff-brief.md. Folge dabei .agents/vorgehen/04-kontext.md.
```

```text
/new
```

Im neuen Chat:

```text
Lies .agents/state/handoff-brief.md. Vergleiche den Inhalt mit den Dateien im Projekt und mit git status. Nenne mir dann die naechste offene Aufgabe.
```

```text
Baue: den Plan .agents/tasks/board.md. Baue alle offenen Aufgaben dieses Plans, eine nach der anderen, ohne zwischendurch anzuhalten. Fang bei der ersten offenen Aufgabe an.
```

Wenn Codex meldet, dass alle Aufgaben fertig sind, im zweiten Terminal im Ordner
`task-board`, nacheinander:

```text
npm test
npm run dev
```

Danach im Browser drei Spalten, Karte anlegen, Neuladen, Verschieben und Filter pruefen und
in `.agents/tasks/done/board.md` nachsehen, dass jede Aufgabe abgehakt oder begruendet
durchgestrichen ist. Codex hat den fertigen Plan dorthin verschoben.

#### Schritt 5: Abnahme

Wenn Abnahmepunkt 5 im Browser nicht funktioniert:

```text
Abnahmepunkt 5 geht nicht. Ich waehle mit Tab eine Karte in der Spalte Offen und nehme sie mit der Leertaste auf. Dann druecke ich die Pfeiltaste nach rechts, aber die Karte bleibt in Offen. Schreib zuerst einen Test, der diesen Fehler zeigt, und behebe ihn erst danach.
```

#### Schritt 6: Optional: automatische Browser-Tests

```text
Referenzen: playwright
```

Wenn in der Antwort kein `FEHLT` steht:

```text
Schreibe Playwright-Tests fuer diese sechs Punkte und fuehre sie aus. Nutze dafuer die Playwright-Vorlage aus .agents/references/INDEX.md. Behebe gefundene Fehler, aber baue keine neuen Funktionen.
1. Beim Tippen im Dialog bleibt der Cursor im richtigen Feld.
2. Jede Karte zeigt im Dialog ihre eigenen Werte, auch nach dem Wechsel zu einer anderen Karte.
3. Verschieben geht mit Tab, Leertaste und Pfeiltasten. Ein unsichtbarer Text fuer Screenreader meldet jeden Schritt.
4. Alle Knoepfe, Felder und der Dialog haben einen Namen fuer Screenreader.
5. Der Fokus bleibt im offenen Dialog und springt beim Schliessen zurueck zur Karte.
6. Beim Anlegen, Verschieben, Bearbeiten und Filtern erscheinen keine Fehler in der Browser-Konsole.
```

## Entscheidungen aus dem Brainstorm

| Frage | Erwartete Entscheidung |
|---|---|
| Volle Spalte | Die Spalte warnt sichtbar ab einem festgelegten Limit. Das Verschieben bleibt moeglich. |
| Filter und Verschieben | Der Filter aendert nur die Sicht. Verschieben aendert die echte Spaltenzuordnung; ausgeblendete Karten bleiben in ihrer Reihenfolge. |
| Zwei Browserfenster | Keine Live-Synchronisation. Der zuletzt gespeicherte Stand wird beim naechsten Neuladen gelesen. |

## Erwartete Planstruktur

1. Vite-, React- und TypeScript-Projekt erstellen; Datenmodell und lokale Speicherung mit Unit-Tests.
2. Board, Spalten, Kartenanzeige und Leerzustaende bauen.
3. Karten anlegen sowie Detail-Dialog mit Bearbeiten und Schutz vor ungespeichertem Schliessen bauen.
4. Maus-Verschieben mit sichtbarem Ziel bauen.
5. Tastatur-Verschieben mit Live-Meldung bauen.
6. Prioritaets- und Textfilter bauen.
7. Fehlerhafte gespeicherte Daten behandeln.

Jede Aufgabe ist klein genug, um einzeln gebaut und getestet zu werden. Jede Aufgabe hat Kriterien im Muster "Wenn X, dann Y".

## Erwartete Vorlagen

| Aufgabe | Slug und Datei aus `references/INDEX.md` |
|---|---|
| 1 | `zustand`: `docs/reference/middlewares/persist.md`, `tests/persistSync.test.tsx`; `vitest`: `examples/basic/vite.config.ts` |
| 2, 4 | `dnd-kit`: `MultipleContainers.tsx`, `stories/components/Container/`, `stories/components/Item/` |
| 3 | `shadcn`: `dialog.tsx`, `select.tsx`, `input.tsx`, `textarea.tsx` |
| 5 | `dnd-kit`: `multipleContainersKeyboardCoordinates.ts`, `Accessibility/defaults.ts` |
| 6 | `shadcn`: `select.tsx`, `input.tsx` |
| 7 | `zustand`: `persisting-store-data.md` |
| Tests nach Rolle und Namen | `testing-library`: `byrole.mdx`. Im Brief gewaehlt und in Schritt 2 mit den anderen Slugs geholt. |
| Optionale Browser-Tests | `playwright`: `examples/todomvc/`. Nicht im Brief, erst im optionalen Schritt 6 geholt. |

Ein Eintrag steht nur in `INDEX.md`, wenn die Teilnehmenden den Slug in Schritt 1 fuer ein Problem gewaehlt haben, der Brief ihn nennt und sie ihn in Schritt 2 geholt haben. Ausnahme ist `playwright` im optionalen Schritt 6. Ein Plan, der fuer die schwierigen Teile keine Vorlage nennt und alles neu schreiben laesst, hat die Referenzliste nicht genutzt.

## Mindestabnahme

- Drei sichtbare Spalten und Karten mit Titel, Beschreibung und Prioritaet.
- Anlegen, Bearbeiten, Maus- und Tastatur-Verschieben.
- Filter, Persistenz, Leer- und Fehlerzustaende.
- Die Entscheidungen aus dem Brainstorm sind als Kriterien im Plan und im Verhalten sichtbar.

## Optionales Quality Gate

Playwright prueft die sechs Punkte aus Schritt 6: Cursor beim Tippen im Dialog, eigene Dialogwerte je Karte, Tastaturbedienung mit Screenreader-Meldung, zugaengliche Namen, Dialog-Fokus und Konsolenfehler. Danach folgt ein manueller Browser-Check.
