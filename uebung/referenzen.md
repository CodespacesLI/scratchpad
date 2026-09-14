# Referenzen zur Übung

Alle Angaben per GitHub-API geprüft am **13.09.2026**. Lizenz und letzter Push stehen so
da, wie die API sie an dem Tag gemeldet hat. Wo GitHub die Lizenz nicht automatisch
erkennt (`Other` in der API), steht hier, was in der LICENSE-Datei wirklich drin steht.

Die Repos sind zum **Nachschlagen** da, nicht zum Abschreiben. In der Plan-Phase ersetzt
diese Liste die Codebase-Erkundung, die auf grüner Wiese ins Leere läuft.

---

## Drag-and-Drop mit Tastaturbedienung

### atlassian/pragmatic-drag-and-drop

- <https://github.com/atlassian/pragmatic-drag-and-drop>
- Lizenz: **Apache-2.0** (die API meldet `Other`, die LICENSE-Datei ist der
  Apache-2.0-Text mit Copyright Atlassian 2024)
- Letzter Push: 2026-09-12, nicht archiviert, rund 12.8k Sterne

**Wo hineinschauen:** die Pakete `react-accessibility` und `live-region` im Ordner
`packages/`. Genau dort steckt der Teil, den fast jede Drag-and-Drop-Anleitung im Netz
auslässt. Zusätzlich `packages/react-drop-indicator` für die Frage, wie man vor dem
Loslassen zeigt, wo die Karte landet.

**Die Frage, die du hier beantwortet bekommst:** Wie sieht ein Verschiebe-Vorgang aus,
der ohne Maus funktioniert, und was genau wird dabei an einen ARIA-Live-Bereich
gemeldet, damit ein Screenreader den Zwischenstand ansagt?

### clauderic/dnd-kit

- <https://github.com/clauderic/dnd-kit>
- Lizenz: **MIT**
- Letzter Push: 2026-09-12, nicht archiviert, rund 17.6k Sterne

**Achtung, das ist der Stolperstein:** der `main`-Branch trägt die nächste Hauptversion
(`@dnd-kit/react` 0.5.0, veröffentlicht 2026-06-11, Ordner `packages/react`,
`packages/abstract`, `packages/dom`). Das ist nicht dasselbe wie das stabile
`@dnd-kit/core` in Version 6, auf das sich praktisch jedes Tutorial bezieht. Wenn du
Code aus `main` liest und `@dnd-kit/core` installierst, passen die Namen nicht zusammen.
Entscheide dich für eine der beiden Linien und halte dich daran.

**Die Frage, die du hier beantwortet bekommst:** Wie ist ein Sensor aufgebaut, der aus
Tastendrücken dieselben Verschiebe-Ereignisse macht wie ein Zeiger, und wie hält er
fest, welche Spalte gerade das Ziel ist?

### hello-pangea/dnd

- <https://github.com/hello-pangea/dnd>
- Lizenz: **Apache-2.0** (API meldet `Other`, LICENSE ist Apache-2.0, Copyright Gabriel
  Santerre 2021 und Atlassian 2019)
- Letzter Push: 2026-09-13, nicht archiviert, rund 4k Sterne

**Wo hineinschauen:** nur zum Vergleich, wenn dir die beiden oberen zu tief liegen. Das
ist der gepflegte Fork von `react-beautiful-dnd` und die einzige lebende Fassung dieser
API. Sein Modell aus `DragDropContext`, `Droppable` und `Draggable` ist schneller zu
lesen, dafür weniger flexibel.

**Die Frage, die du hier beantwortet bekommst:** Wie sieht die minimal mögliche
Board-Struktur aus, wenn man die Bibliothek die ganze Arbeit machen lässt?

## Komponenten und Design-System

### shadcn-ui/ui

- <https://github.com/shadcn-ui/ui>
- Lizenz: **MIT**
- Letzter Push: 2026-09-12, nicht archiviert, rund 124k Sterne

**Wo hineinschauen:** die Dialog-Komponente und die Formularfelder. Der Code wird nicht
als Abhängigkeit installiert, sondern in dein Projekt kopiert, also liest du hier genau
das, was danach bei dir steht.

**Die Frage, die du hier beantwortet bekommst:** Wie ist ein Dialog aufgebaut, der den
Fokus fängt, ihn beim Schliessen an den Auslöser zurückgibt und einen zugänglichen Namen
trägt, ohne dass du dafür selbst Fokus-Logik schreibst?

### radix-ui/primitives

- <https://github.com/radix-ui/primitives>
- Lizenz: **MIT**
- Letzter Push: 2026-08-08, nicht archiviert, rund 19.3k Sterne

**Wo hineinschauen:** die Quelle unter dem Dialog von shadcn. Relevant sind der Dialog
selbst und die Bausteine für Auswahlfelder, weil der Prioritätsfilter eines braucht.

**Die Frage, die du hier beantwortet bekommst:** Welche ARIA-Attribute setzt eine
Bibliothek, die das ernst nimmt, und welche davon musst du in deiner Playwright-Spec
abfragen, statt auf sichtbaren Text zu prüfen?

## Zustand und lokale Persistenz

### pmndrs/zustand

- <https://github.com/pmndrs/zustand>
- Lizenz: **MIT**
- Letzter Push: 2026-09-11, nicht archiviert, rund 58.7k Sterne

**Wo hineinschauen:** `src/middleware/persist.ts`. Diese eine Datei beantwortet die
Persistenz-Fragen der Übung.

**Die Frage, die du hier beantwortet bekommst:** Wann genau wird geschrieben, was
passiert beim Lesen eines beschädigten oder veralteten Stands, und wie hängt man sich in
Änderungen aus einem zweiten Browser-Tab ein? Wer den dritten zitierten Satz aus dem
Auftrag ernst nimmt, findet die Antwort hier und nicht in der README.

## Fachliche Vorlage: echte Kanban-Produkte

### wekan/wekan

- <https://github.com/wekan/wekan>
- Lizenz: **MIT**
- Letzter Push: 2026-09-13, nicht archiviert, rund 21.1k Sterne

**Wo hineinschauen:** nicht in den Code, der ist Meteor und hilft dir technisch nicht.
Hineinschauen in die Screenshots, die Dokumentation zu Limits pro Spalte und in die
Issue-Liste zum Thema Filter.

**Die Frage, die du hier beantwortet bekommst:** Was macht ein ausgereiftes Board, wenn
eine Spalte ihr Limit erreicht: blockiert es das Ablegen, oder färbt es die Spalte nur
ein? Genau der Zielkonflikt aus dem ersten zitierten Satz des Auftrags, und du siehst
dort, welchen Preis jede Seite hat.

### plankanban/planka

- <https://github.com/plankanban/planka>
- Lizenz: **PLANKA Community License 1.1** (Stand 20.05.2025, kein OSI-Standard, die API
  meldet deshalb `Other`). Es gibt daneben eine kommerzielle Lizenz.
- Letzter Push: 2026-09-13, nicht archiviert, rund 12.5k Sterne

**Lizenz-Hinweis, ernst gemeint:** das ist keine MIT- oder Apache-Lizenz. Lies den Code
zum Verstehen, übernimm keine Ausschnitte in dein Übungsprojekt, ohne die Lizenz gelesen
zu haben.

**Wo hineinschauen:** das Frontend ist React. Interessant sind die Board-Ansicht und die
Karten-Detailansicht.

**Die Frage, die du hier beantwortet bekommst:** Wie schneidet ein React-Board seinen
Zustand, damit das Verschieben einer Karte nicht das ganze Board neu rendert, und wie
sieht die Datenform einer Karte aus, wenn das Produkt über Jahre gewachsen ist?

## Playwright-Testmuster

### microsoft/playwright

- <https://github.com/microsoft/playwright>
- Lizenz: **Apache-2.0**
- Letzter Push: 2026-09-11, nicht archiviert, rund 96k Sterne

**Wo hineinschauen:** der Ordner `examples/todomvc`. Er enthält `playwright.config.ts`,
einen Ordner `specs` und einen Ordner `tests`. Das ist eine vollständige, gepflegte
Suite gegen eine Listen-Oberfläche, also gegen fast dasselbe Problem wie dein Board.

**Die Frage, die du hier beantwortet bekommst:** Wie formuliert man eine Erwartung an
eine Liste, die sich beim Tippen ändert, ohne mit festen Wartezeiten zu arbeiten, und
wie trennt man Spezifikation von Testdatei so, dass beide lesbar bleiben?

### vitest-dev/vitest

- <https://github.com/vitest-dev/vitest>
- Lizenz: **MIT**
- Letzter Push: 2026-09-13, nicht archiviert, rund 17.1k Sterne

**Wo hineinschauen:** der Ordner `examples`, dort `basic` und `projects`. Am 13.09.2026
liegt dort **kein** React-Beispiel (der Ordner enthält `basic`, `fastify`,
`in-source-test`, `lit`, `opentelemetry`, `profiling`, `projects`, `typecheck`). Die
React-Verdrahtung liest du deshalb aus `examples/basic` plus der Konfiguration im
`test`-Block der Vite-Config.

**Die Frage, die du hier beantwortet bekommst:** Wie verdrahtet man Vitest in eine
bestehende Vite-Konfiguration, ohne eine zweite Build-Kette aufzumachen, und welche
Umgebung braucht ein Test, der die Speicherschicht des Browsers anfasst?

### testing-library/react-testing-library

- <https://github.com/testing-library/react-testing-library>
- Lizenz: **MIT**
- Letzter Push: 2026-08-27, nicht archiviert, rund 19.6k Sterne

**Wo hineinschauen:** die Abfragen nach Rolle und zugänglichem Namen.

**Die Frage, die du hier beantwortet bekommst:** Wie fragt man ein Element über seine
Rolle und seinen zugänglichen Namen ab statt über eine CSS-Klasse, sodass derselbe
Test-Stil in Vitest und in Playwright funktioniert und das Qualitätskriterium
„zugänglicher Name" nebenbei mitgeprüft wird?

---

## Geprüft und bewusst nicht empfohlen

- **atlassian/react-beautiful-dnd**: **archiviert** (Stand 13.09.2026), letzter Push
  2025-08-18, trotz rund 34k Sternen. Atlassian verweist auf
  `pragmatic-drag-and-drop`. Die meisten Tutorials im Netz zeigen noch diese Bibliothek.
  Nicht benutzen. Wer die alte API will, nimmt `hello-pangea/dnd` oben.
- **mattermost/focalboard**: die Adresse leitet weiter auf
  `mattermost-community/focalboard`. Formal nicht archiviert, letzter Push aber
  2026-05-18, also rund vier Monate still. Als lebende Vorlage zu ruhig, deshalb steht
  `wekan` oben.
- **go-vikunja/vikunja**: lebt (Push 2026-09-13), aber AGPL-3.0 und ein Vue-Frontend auf
  einem Go-Backend. Für ein React-Board ohne Server kein Gewinn, und die AGPL ist für ein
  Übungsprojekt eine unnötige Frage.
- **kanboard/kanboard**: lebt (MIT, Push 2026-09-11), ist aber PHP mit serverseitig
  gerendertem Frontend. Fachlich brauchbar, technisch für diese Übung ohne Nutzen, und
  `wekan` deckt die fachliche Seite schon ab.

## Unsicher, selbst nachsehen

- Die Ordnerstruktur von `dnd-kit` auf `main` ist die der neuen Hauptversion. Ob die zum
  Zeitpunkt deiner Schulung schon als stabil gilt, prüfst du an den Releases im Repo,
  nicht an diesem Blatt.
- `microsoft/playwright` verschiebt seine Beispiele gelegentlich. Findest du
  `examples/todomvc` nicht, sieh im Ordner `examples` nach, was stattdessen dort liegt.
