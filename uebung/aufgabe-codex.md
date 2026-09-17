# Uebung: Task-Board mit Codex

Du baust mit Codex eine kleine Web-App. Den Code schreibt Codex. Du sagst Codex,
was es tun soll, und pruefst das Ergebnis.

So arbeitest du mit diesem Blatt:

- Jeder Schritt hat nummerierte Unterschritte. Bearbeite sie der Reihe nach.
- Deine Nachrichten an Codex schreibst du selbst. Fest steht nur das Wort am Anfang,
  zum Beispiel `Plane:`. Alles dahinter formulierst du in eigenen Worten.
- Die Liste „Deine Nachricht enthaelt:“ nennt, was in deine Nachricht gehoert.
  Schick die Nachricht mit Enter ab.
- Passt ein Ergebnis nicht, sag Codex genau, was fehlt oder falsch ist.

## Was gebaut wird

- Drei Spalten: Offen, In Arbeit, Fertig.
- Eine Karte hat einen Titel, eine Beschreibung (optional) und eine Prioritaet.
- Karten lassen sich mit der Maus und mit der Tastatur in eine andere Spalte verschieben.
- Ein Klick auf eine Karte oeffnet ein Fenster (Dialog) zum Bearbeiten.
- Filter nach Prioritaet und nach einem Wort im Titel.
- Nach dem Neuladen der Seite ist alles noch da.
- Eine leere Spalte zeigt einen Hinweis. Kaputte gespeicherte Daten zeigen eine Meldung.

Nicht bauen: Login, Server, Synchronisation, eigene Spalten, Anhaenge, Kommentare,
Termine, Sortieren innerhalb einer Spalte, Farbthemen, Handy-Ansicht, Veroeffentlichen.

## Vorlagen fuer die schwierigen Teile

Fuer die schwierigen Teile gibt es fertigen, getesteten Code auf GitHub. Codex baut diese
Teile spaeter mit diesem Code. Das spart Zeit.

In Schritt 1, Anforderungen klaeren, fragt Codex dich nach Vorlagen. Du waehlst dann die
Slugs aus der Tabelle unten. In Schritt 2, Vorlagen holen, laedst du den Code mit
`Referenzen: <slug>` herunter.

Im Kurs kennt `Referenzen:` nur die Slugs aus der Tabelle unten. Welche Dateien es aus einem
Repository holt, ist fest vorgegeben. Die Tabelle steht auch in
`.agents/references/referenzen.md`.

So laeuft `Referenzen: <slug>` ab:

1. Der Code landet unter `.agents/references/sources/<slug>/`.
2. Codex schreibt fuer jede geholte Datei den Pfad und eine Erklaerung, wofuer sie gut
   ist, in `.agents/references/INDEX.md`.
3. Beim Planen (`Plane:`) schaut Codex gleich zu Beginn in `INDEX.md` nach und weiss so
   bei jedem Problem, wo es dafuer fertigen Code gibt.

Ausserhalb des Kurses wuerde Codex die geholten Dateien selbst lesen und die Erklaerung
selbst schreiben. Im Kurs steht sie schon fest, damit keine ganzen Repositories geladen werden
und der Index bei allen gleich ist.

| Problem | Slug |
|---|---|
| Karten mit Maus und Tastatur zwischen Spalten verschieben | `dnd-kit` |
| Dialog, Auswahlfeld, Eingabefelder | `shadcn` |
| Daten im Browser speichern, kaputte Daten abfangen | `zustand` |
| Unit-Tests einrichten | `vitest` |
| Tests, die Elemente ueber Rolle und Namen finden | `testing-library` |
| Automatische Browser-Tests | `playwright` |

## 0. Vorbereiten

### Voraussetzungen

Waehle einen Weg. Einzelheiten stehen in der [README](../README.md#schnellstart).

**Eigener Rechner.**

1. Oeffne ein Terminal im Ordner `scratchpad`.
2. Tippe den Befehl fuer dein System:

   | System | Befehl |
   |---|---|
   | Windows | `.\setup.cmd codex` |
   | Mac oder Linux | `bash setup.sh codex` |

3. Warte, bis der Befehl fertig ist. Am Ende steht „Alles bereit“. Sonst steht dort, was
   fehlt.
4. Schliesse das Terminal und oeffne ein neues.

**Dev Container oder Codespaces.** Alles ist schon installiert. Oeffne das Repo im
Container und oeffne dort ein Terminal.

### Projekt anlegen

1. Oeffne ein Terminal im Ordner `scratchpad`.
2. Tippe diese drei Zeilen nacheinander. Unter Mac und Linux beginnt die erste Zeile mit
   `python3`.

   ```text
   python start.py codex
   cd task-board
   codex
   ```

   Zeile 1 legt den Ordner `task-board` an und kopiert die Anleitungen fuer Codex hinein.
   Die Datei `AGENTS.md` erklaert Codex die Woerter `Brainstorm:`, `Referenzen:`, `Plane:`
   und `Baue:`. Zeile 2 wechselt in diesen Ordner. Zeile 3 startet Codex.
3. Melde dich beim ersten Start einmal an.

**Wichtig:** Bleib von Schritt 1 bis Schritt 4 im selben Chat. Codex weiss nur, was im
aktuellen Chat besprochen wurde. Einen frischen Chat startest du nur in Schritt 4, wenn
der Chat rund 120 000 Tokens erreicht. Der Warnkasten dort erklaert, warum.

## 1. Anforderungen klaeren

**Ziel:** Codex zeigt einen kurzen Brief, der die App beschreibt und deine Vorlagen nennt.
Code gibt es noch nicht.

1. Schreib `Brainstorm:` und dahinter deine Nachricht.

   **Deine Nachricht enthaelt:**
   - Was die App koennen soll (Liste „Was gebaut wird“).
   - Was nicht gebaut wird.
   - Dass Codex dich zu diesen drei Punkten fragen soll:
     - Was passiert, wenn eine Spalte sehr viele Karten hat?
     - Ein Filter ist aktiv und du verschiebst eine Karte. Was passiert?
     - Die App ist in zwei Browserfenstern gleichzeitig offen. Was passiert?

2. Warte auf die Fragen von Codex. Beantworte jede Frage in eigenen Worten. Triff zu
   jedem der drei Punkte selbst eine Entscheidung und schreib Codex alle drei
   Entscheidungen.
3. Such fuer jeden schwierigen Teil in der Tabelle „Vorlagen“ das passende Problem. Lass
   `playwright` fuer den optionalen Schritt 6 aus. Codex fragt dich nach fertigem Code fuer
   die schwierigen Teile. Schreib Codex dazu eine Nachricht.

   **Deine Nachricht enthaelt:**
   - Jeden Slug, den du gewaehlt hast.
   - Zu jedem Slug das Problem, das er loesen soll.

4. Warte, bis Codex den Brief zeigt. Pruefe:
   - [ ] Codex zeigt einen Brief.
   - [ ] Deine drei Entscheidungen stehen darin.
   - [ ] Der Brief nennt deine gewaehlten Slugs, jeden mit dem Problem, das er loest.
5. Passt der Brief, schreib Codex, dass er so passt.

## 2. Vorlagen holen

**Ziel:** Der fertige Code fuer die Slugs aus deinem Brief liegt im Projekt, und
`.agents/references/INDEX.md` nennt ihn.

1. Schreib `Referenzen:` und dahinter alle Slugs, die dein Brief nennt, zum Beispiel
   `Referenzen: dnd-kit shadcn`.
2. Warte, bis Codex fertig ist. Pruefe:
   - [ ] In der Antwort steht kein `FEHLT`.
   - [ ] Die Datei `.agents/references/INDEX.md` nennt jeden Slug aus deinem Brief.

## 3. Plan erstellen

**Ziel:** Die Datei `.agents/tasks/board.md` enthaelt eine Liste kleiner Aufgaben. Die
schwierigen Aufgaben nennen eine Vorlage.

1. Schreib `Plane:` und dahinter deine Nachricht.

   **Deine Nachricht enthaelt:**
   - Welcher Brief gilt: der aus Schritt 1 in diesem Chat.
   - Unter welchem Namen der Plan gespeichert wird: `board.md`.
   - Dass Codex in `.agents/references/INDEX.md` nachschauen soll, wo es fertigen Code
     fuer die schwierigen Teile gibt.

2. Warte, bis Codex den Plan zeigt.
3. Oeffne die Datei `.agents/tasks/board.md`. Pruefe:
   - [ ] Jede Aufgabe hat 1 bis 3 Saetze der Form „Wenn ..., dann ...“.
   - [ ] Die schwierigen Aufgaben haben eine Zeile „Vorlage:“.
   - [ ] Deine drei Entscheidungen aus Schritt 1 stehen als „Wenn ..., dann ...“ im Plan.
4. Passt der Plan, schreib Codex, dass er freigegeben ist.

## 4. Bauen

**Ziel:** Alle Aufgaben im Plan sind erledigt, und die App laeuft im Browser.

1. Schreib `Baue:` und dahinter deine Nachricht.

   **Deine Nachricht enthaelt:**
   - Welcher Plan gilt: `.agents/tasks/board.md`.
   - Dass Codex alle offenen Aufgaben des Plans am Stueck baut, ohne
     zwischendurch anzuhalten.

2. Warte, bis Codex meldet, dass es fertig ist. Das dauert eine ganze Weile.

> [!WARNING]
> **Wann startest du einen frischen Chat?** In einem langen Chat wird Codex schon ab etwa
> 100 000 Tokens spuerbar ungenauer, lange bevor der Chat technisch voll ist. Deshalb
> wechselst du schon bei rund 120 000 Tokens in einen frischen Chat. Mit diesem Abstand
> baut Codex die laufende Aufgabe noch sauber fertig. Der frische Chat uebernimmt den
> Stand aus einer Datei. Das ist Context Engineering in einfacher Form.
> Bei Codex gibt es keinen Waechter, der mitzaehlt. Du schaust deshalb selbst hin. Der
> Befehl `/status` zeigt die Tokenzahl. Codex hat auch keine fertigen Befehle fuer den
> Wechsel. Du machst ihn in vier Schritten und beginnst jeden erst, wenn Codex mit dem
> vorigen fertig ist:
>
> 1. Schreib Codex eine Nachricht. Sie enthaelt: Codex schreibt den aktuellen Stand in die
>    Datei `.agents/state/handoff-brief.md` und folgt dabei `.agents/vorgehen/04-kontext.md`.
> 2. Tippe `/new`. Codex startet einen neuen, leeren Chat.
> 3. Schreib im neuen Chat eine Nachricht. Sie enthaelt: Codex liest
>    `.agents/state/handoff-brief.md`, vergleicht den Inhalt mit den Dateien und
>    `git status` und nennt die naechste offene Aufgabe.
> 4. Schreib `Baue:` und dahinter dieselben Inhalte wie in Unterschritt 1 von Schritt 4.
>    Codex macht bei der ersten offenen Aufgabe weiter.
>
> Warte danach wieder, bis Codex meldet, dass es fertig ist.

3. Oeffne ein zweites Terminal im Ordner `task-board`. Tippe `npm test`. Pruefe:
   - [ ] Am Ende stehen keine roten Fehler.
4. Tippe im zweiten Terminal `npm run dev`. Oeffne die Adresse, die dort steht, im
   Browser. Meist ist das `http://localhost:5173`. Pruefe:
   - [ ] Du siehst drei Spalten und kannst eine Karte anlegen.
   - [ ] Nach dem Neuladen ist die Karte noch da.
   - [ ] Du kannst eine Karte in eine andere Spalte verschieben.
   - [ ] Der Filter blendet Karten aus und wieder ein.
5. Gehen die beiden Befehle nicht, frag Codex, wie du die Tests und die App startest.
6. Oeffne die Datei `.agents/tasks/done/board.md`. Codex hat den fertigen Plan dorthin
   verschoben. Pruefe:
   - [ ] Jede Aufgabe ist abgehakt (`[x]`) oder durchgestrichen und hat einen Grund
         dabei.

## 5. Abnahme

**Ziel:** Jeder Punkt unten funktioniert. Es zaehlt nur, was du selbst im Browser
pruefst.

1. Tippe im zweiten Terminal `npm test`, danach `npm run dev`. Oeffne die App im Browser.
2. Pruefe jeden Punkt:
   - [ ] 1. Beim ersten Oeffnen sind die Spalten Offen, In Arbeit und Fertig zu sehen.
   - [ ] 2. Eine leere Spalte zeigt einen Text und einen Knopf zum Anlegen einer Karte.
   - [ ] 3. Eine neue Karte erscheint unten in der gewaehlten Spalte.
   - [ ] 4. Beim Ziehen mit der Maus ist vorher zu sehen, wo die Karte landet. Sie landet
         unten in der Zielspalte.
   - [ ] 5. Tastatur: Tab waehlt eine Karte. Leertaste nimmt sie auf. Pfeiltasten
         wechseln die Spalte. Leertaste legt sie ab.
   - [ ] 6. Im Dialog lassen sich Titel, Beschreibung und Prioritaet aendern. Schliesst
         du ihn mit ungespeicherten Aenderungen, fragt die App nach.
   - [ ] 7. Prioritaetsfilter und Wortfilter wirken gleichzeitig. Die
         Spaltenueberschriften bleiben sichtbar.
   - [ ] 8. Nach dem Neuladen sind alle Karten in derselben Spalte und Reihenfolge.
   - [ ] 9. Kaputte gespeicherte Daten zeigen ein leeres Board mit einer verstaendlichen
         Meldung. So testest du das: Oeffne die Browser-Entwicklertools (F12). Klicke
         auf den Reiter „Application“ und dann auf Local Storage. Ersetze den Wert durch
         `kaputt` und lade die Seite neu.
   - [ ] 10. Deine drei Entscheidungen aus Schritt 1 funktionieren so, wie du sie
         beschrieben hast.
3. Geht ein Punkt nicht, schreib Codex eine Nachricht.

   **Deine Nachricht enthaelt:**
   - Welcher Abnahmepunkt nicht geht (die Nummer).
   - Was du genau siehst.
   - Dass Codex zuerst einen Test schreibt, der den Fehler zeigt, und den Fehler erst
     danach behebt (Test Driven Development).

4. Pruefe den Punkt danach noch einmal im Browser.

## 6. Optional: automatische Browser-Tests

Bearbeite diesen Schritt nur, wenn noch Zeit ist.

**Ziel:** Automatische Browser-Tests fuer sechs Punkte laufen ohne Fehler.

1. Schreib `Referenzen: playwright`. Codex holt als Vorlage nur die fertigen Beispiel-Tests
   aus dem Playwright-Repository auf GitHub. Die Beispiele testen, wie eine Todo-App
   Eintraege anlegt, bearbeitet und filtert. Diese drei Funktionen hat dein Task-Board
   auch. Warte, bis Codex fertig ist. In der Antwort darf kein `FEHLT` stehen.
2. Schreib Codex eine Nachricht ohne Wort am Anfang.

   **Deine Nachricht enthaelt:**
   - Dass Codex Playwright-Tests fuer die sechs Punkte unten schreiben und ausfuehren
     soll.
   - Dass es die Playwright-Vorlage aus `.agents/references/INDEX.md` nutzen soll.
   - Dass es gefundene Fehler behebt und **keine** neuen Funktionen baut.

   Die sechs Punkte:
   1. Beim Tippen im Dialog bleibt der Cursor im richtigen Feld.
   2. Jede Karte zeigt im Dialog ihre eigenen Werte, auch nach dem Wechsel zu einer
      anderen Karte.
   3. Verschieben geht mit Tab, Leertaste und Pfeiltasten. Ein unsichtbarer Text fuer
      Screenreader meldet jeden Schritt.
   4. Alle Knoepfe, Felder und der Dialog haben einen Namen fuer Screenreader.
   5. Der Fokus bleibt im offenen Dialog und springt beim Schliessen zurueck zur Karte.
   6. Beim Anlegen, Verschieben, Bearbeiten und Filtern erscheinen keine Fehler in der
      Browser-Konsole.

3. Warte, bis Codex fertig ist. Pruefe:
   - [ ] Codex meldet, dass alle Tests ohne Fehler durchlaufen.
4. Pruefe die App danach noch einmal selbst im Browser.
