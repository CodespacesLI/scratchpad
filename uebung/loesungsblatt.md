# Loesungsblatt: Task-Board

Dieses Blatt beschreibt eine erwartete Loesung. Andere Loesungen sind gueltig, wenn sie den Abnahmekriterien entsprechen und begruendet sind.

## Beispiel-Nachrichten

Nur fuer die Kursleitung oder zum Vergleich nach der Uebung. Die Teilnehmenden
formulieren ihre Nachrichten selbst. Diese Beispiele zeigen, was eine gute Nachricht
enthaelt.

**Claude:**

| Schritt | Beispiel |
|---|---|
| 1 | `/brainstorm Lokales Task-Board fuer eine Person. Drei Spalten: Offen, In Arbeit, Fertig. Karten mit Titel, optionaler Beschreibung und Prioritaet. Verschieben mit Maus und Tastatur, Dialog zum Bearbeiten, Filter nach Prioritaet und Titelwort, Speichern im Browser. Leere Spalten und kaputte Daten zeigen eine Meldung. Nicht bauen: Login, Server, Synchronisation, eigene Spalten, Anhaenge, Kommentare, Termine, Sortieren in einer Spalte, Themen, Handy-Ansicht, Veroeffentlichen.` |
| 2 | `/ref dnd-kit shadcn zustand vitest testing-library` |
| 2 | `/plan Nimm den Brief aus diesem Chat. Lies .claude/references/INDEX.md und trage bei jeder Aufgabe mit passender Datei eine Vorlage ein. Fehlt fuer einen schwierigen Teil eine Vorlage, nenne mir den Slug. Speichere den Plan als .claude/tasks/board.md.` |
| 3 | `/build .claude/tasks/board.md Baue nur: Projekt anlegen, Board mit drei Spalten, Karten anlegen, Dialog, Speichern im Browser, Hinweis bei leerer Spalte. Verschieben und Filter noch nicht.` |
| 4 | `/handoff`, dann `/clear`, dann `/resume` |
| 5 | `/build .claude/tasks/board.md Baue die restlichen offenen Aufgaben: Maus-Verschieben, Tastatur-Verschieben, Filter, Verhalten bei vielen Karten.` |
| 6 | `Abnahmepunkt 5 geht nicht: Nach der Leertaste bewegen die Pfeiltasten die Karte nicht. Schreib zuerst einen Test, der das zeigt, dann behebe es.` |
| 7 | `/ref playwright` |
| 7 | `Schreibe Playwright-Tests fuer diese sechs Punkte und fuehre sie aus: <Punkte>. Nutze die Playwright-Vorlage aus .claude/references/INDEX.md. Behebe gefundene Fehler, baue keine neuen Funktionen.` |

**Codex:** gleiche Inhalte mit diesen Unterschieden:

| Claude | Codex |
|---|---|
| `/ref <slug> ...` | `Referenzen: <slug> ...` |
| `/brainstorm ...` | `Brainstorm: ...` |
| `/plan ...` | `Plane: ...` |
| `/build .claude/tasks/board.md ...` | `Baue: den Plan .agents/tasks/board.md. ...` |
| `.claude/...` | `.agents/...` |
| `/handoff` | `Schreibe den aktuellen Stand nach .agents/state/handoff-brief.md. Folge dabei .agents/vorgehen/04-kontext.md.` |
| `/clear` | `/new` |
| `/resume` | `Lies .agents/state/handoff-brief.md, vergleiche ihn mit den Dateien und git status und nenne die naechste offene Aufgabe.` |

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
| Optionale Browser-Tests | `playwright`: `examples/todomvc/`; `testing-library`: `byrole.mdx`. Erst in Schritt 7 geholt. |

Ein Plan, der fuer die schwierigen Teile keine Vorlage nennt und alles neu schreiben laesst, hat die Referenzliste nicht genutzt.

## Mindestabnahme

- Drei sichtbare Spalten und Karten mit Titel, Beschreibung und Prioritaet.
- Anlegen, Bearbeiten, Maus- und Tastatur-Verschieben.
- Filter, Persistenz, Leer- und Fehlerzustaende.
- Die Entscheidungen aus dem Brainstorm sind als Kriterien im Plan und im Verhalten sichtbar.

## Optionales Quality Gate

Playwright prueft Fokus, Tastaturbedienung, zugaengliche Namen, Dialog-Fokus und Konsolenfehler. Danach folgt ein manueller Browser-Check.
