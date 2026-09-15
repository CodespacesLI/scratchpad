# Uebung: Task-Board mit Claude Code

Du baust mit Claude Code eine kleine Web-App. Du schreibst keinen Code selbst. Du sagst
Claude, was es tun soll, und pruefst das Ergebnis.

Zu jedem Schritt steht hier:

- **Ziel:** Was am Ende da sein muss.
- **Befehl:** Womit deine Nachricht anfaengt.
- **Das muss Claude wissen:** Was in deine Nachricht gehoert. Die Worte waehlst du selbst.
- **Pruefe:** Woran du siehst, dass es geklappt hat.

Passt ein Ergebnis nicht, sag Claude genau, was fehlt oder falsch ist. Auch das gehoert
zur Uebung.

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

## Vorlagen: fertiger Code statt neu schreiben

Fuer die schwierigen Teile gibt es fertigen, getesteten Code auf GitHub. Du musst ihn
nicht suchen. Die Liste steht schon in `.claude/references/referenzen.md`:

| Problem | Slug |
|---|---|
| Karten mit Maus und Tastatur zwischen Spalten verschieben | `dnd-kit` |
| Dialog, Auswahlfeld, Eingabefelder | `shadcn` |
| Daten im Browser speichern, kaputte Daten abfangen | `zustand` |
| Unit-Tests einrichten | `vitest` |
| Tests, die Elemente ueber Rolle und Namen finden | `testing-library` |
| Automatische Browser-Tests | `playwright` |

Du holst eine Vorlage erst, wenn du an das Problem kommst: beim Planen oder beim Bauen.

**Befehl:** `/ref`, dahinter ein oder mehrere Slugs mit Leerzeichen getrennt.

Das passiert:

1. Claude laedt nur die Dateien dieser Slugs von GitHub herunter.
2. Die Dateien landen im Ordner `.claude/references/sources/`.
3. Claude ergaenzt die Datei `.claude/references/INDEX.md`. Darin steht, welche Datei
   wofuer die Vorlage ist.

**Pruefe:** In Claudes Antwort steht kein `FEHLT`.

Warum: Fertigen Code zu kopieren und anzupassen geht schneller und macht weniger Fehler,
als alles neu schreiben zu lassen.

## 0. Vorbereiten

### Voraussetzungen

Waehle einen Weg. Einzelheiten stehen in der [README](../README.md#schnellstart).

**Eigener Rechner.** Im Ordner `scratchpad`:

| System | Befehl |
|---|---|
| Windows | `.\setup.cmd claude` |
| Mac oder Linux | `bash setup.sh claude` |

**Pruefe:** Am Ende steht „Alles bereit“. Sonst steht dort, was fehlt. Danach ein neues
Terminal oeffnen.

**Dev Container oder Codespaces.** Alles ist schon installiert. Oeffne das Repo im
Container und nimm dort das Terminal.

### Projekt anlegen

Im Ordner `scratchpad`. Unter Mac und Linux heisst der erste Befehl `python3` statt
`python`:

```text
python start.py claude
cd task-board
claude
```

- Zeile 1 legt den Ordner `task-board` an, kopiert die Anleitungen fuer Claude hinein und
  macht ihn zu einem Git-Projekt.
- Zeile 2 wechselt in den Projektordner.
- Zeile 3 startet Claude. Beim ersten Start meldest du dich einmal an.

**Wichtig:** Bleib von Schritt 1 bis Schritt 3 im selben Chat. Claude weiss nur, was im
aktuellen Chat besprochen wurde.

## 1. Anforderungen klaeren

**Ziel:** Claude zeigt einen kurzen Brief, der die App beschreibt. Code gibt es in diesem
Schritt noch nicht.

**Befehl:** `/brainstorm`, direkt dahinter deine Beschreibung.

**Das muss Claude wissen:**

- Was die App koennen soll (Liste oben).
- Was nicht gebaut wird.

Claude stellt dir danach Fragen. Zu diesen drei Punkten musst du eine Entscheidung
treffen. Fragt Claude nicht danach, bring sie selbst ein:

- Was passiert, wenn eine Spalte sehr viele Karten hat?
- Ein Filter ist aktiv und du verschiebst eine Karte. Was passiert?
- Die App ist in zwei Browserfenstern gleichzeitig offen. Was passiert?

**Pruefe:**

- [ ] Claude zeigt einen Brief.
- [ ] Deine drei Entscheidungen stehen darin.
- [ ] Du hast Claude gesagt, dass der Brief so passt.

## 2. Plan erstellen

**Ziel:** In der Datei `.claude/tasks/board.md` steht eine Liste kleiner Aufgaben. Die
schwierigen Aufgaben nennen eine Vorlage.

**a) Schwierige Teile finden.** Lies deinen Brief. Welche Teile sind aufwendig, oder bei
welchen weisst du nicht, wie man sie loest? Schau in der Tabelle „Vorlagen“ oben, ob es
dafuer eine Vorlage gibt.

**b) Diese Vorlagen holen.** Befehl `/ref` mit den Slugs, die du ausgesucht hast.

**c) Plan schreiben lassen.** Befehl: `/plan`, dahinter deine Anweisung.

**Das muss Claude wissen:**

- Welcher Brief gilt: der aus Schritt 1 in diesem Chat.
- Dass es `.claude/references/INDEX.md` lesen soll und passende Dateien bei den Aufgaben
  als Vorlage eintragen soll.
- Dass es dir einen Slug nennen soll, wenn fuer einen schwierigen Teil noch eine Vorlage
  fehlt.
- Wohin der Plan gespeichert wird: `.claude/tasks/board.md`.

Nennt Claude einen fehlenden Slug, hol ihn mit `/ref` und sag Claude, dass es
weitermachen soll.

**Pruefe:** Oeffne die Datei.

- [ ] Jede Aufgabe hat 1 bis 3 Saetze der Form „Wenn ..., dann ...“.
- [ ] Die schwierigen Aufgaben haben eine Zeile „Vorlage:“.
- [ ] Deine drei Entscheidungen aus Schritt 1 stehen als „Wenn ..., dann ...“ im Plan.

Stimmt alles, sag Claude, dass der Plan freigegeben ist.

## 3. Bauen, Teil 1

**Ziel:** Der erste Teil der App laeuft im Browser.

**Befehl:** `/build`, dahinter der Pfad zum Plan und deine Anweisung.

**Das muss Claude wissen:**

- Welcher Plan gilt: `.claude/tasks/board.md`.
- Was jetzt gebaut wird: Projekt anlegen, Board mit drei Spalten, Karten anlegen, Dialog
  zum Bearbeiten, Speichern im Browser, Hinweis bei leerer Spalte.
- Was noch **nicht** gebaut wird: Verschieben und Filter.

**Haengt Claude an einem Problem?** Zum Beispiel: Ein Test wird nach mehreren Versuchen
nicht gruen, oder Claude schreibt etwas selbst, wofuer die Tabelle „Vorlagen“ einen Slug
hat. Dann:

1. Hol die Vorlage mit `/ref <slug>`.
2. Schreib Claude eine Nachricht. **Das muss Claude wissen:** Welche Vorlage jetzt in
   `.claude/references/INDEX.md` liegt, und dass es fuer dieses Problem die Vorlage
   kopieren und anpassen soll.

**Pruefe** in einem zweiten Terminal im Projektordner:

- [ ] `npm test` zeigt am Ende keine roten Fehler.
- [ ] `npm run dev` zeigt eine Adresse, meist `http://localhost:5173`. Oeffne sie im
      Browser.
- [ ] Du siehst drei Spalten und kannst eine Karte anlegen. Nach dem Neuladen ist sie
      noch da.

Gehen die beiden Befehle nicht, frag Claude, wie man Tests und App startet.

## 4. Chat frisch starten

**Ziel:** Ein neuer, leerer Chat, der trotzdem weiss, wo ihr steht.

Warum: Ein langer Chat macht Claude langsamer und ungenauer.

**Befehle,** einzeln nacheinander:

1. `/handoff`: Claude schreibt den Stand in die Datei `.claude/state/handoff-brief.md`.
2. `/clear`: Der Chat wird geleert.
3. `/resume`: Claude liest die Datei und vergleicht sie mit den echten Dateien im
   Projekt.

**Pruefe:**

- [ ] Nach `/resume` nennt Claude die naechste offene Aufgabe.

## 5. Bauen, Teil 2

**Ziel:** Alle Aufgaben im Plan sind erledigt.

**Befehl:** `/build`, dahinter der Pfad zum Plan und deine Anweisung.

**Das muss Claude wissen:**

- Welcher Plan gilt: `.claude/tasks/board.md`.
- Was jetzt gebaut wird: alle restlichen offenen Aufgaben, also Verschieben mit der
  Maus, Verschieben mit der Tastatur, Filter und das Verhalten bei vielen Karten.

Haengt Claude an einem Problem, gehst du vor wie in Schritt 3.

**Pruefe:**

- [ ] In `.claude/tasks/board.md` ist jede Aufgabe abgehakt (`[x]`) oder durchgestrichen
      und hat einen Grund dabei.

## 6. Abnahme

**Ziel:** Jeder Punkt unten funktioniert. Du pruefst selbst im Browser, Code lesen
zaehlt nicht.

Starte vorher im zweiten Terminal `npm test` und `npm run dev`.

- [ ] 1. Beim ersten Oeffnen sind die Spalten Offen, In Arbeit und Fertig zu sehen.
- [ ] 2. Eine leere Spalte zeigt einen Text und einen Knopf zum Anlegen einer Karte.
- [ ] 3. Eine neue Karte erscheint unten in der gewaehlten Spalte.
- [ ] 4. Beim Ziehen mit der Maus ist vorher zu sehen, wo die Karte landet. Sie landet
      unten in der Zielspalte.
- [ ] 5. Tastatur: Tab waehlt eine Karte. Leertaste nimmt sie auf. Pfeiltasten wechseln
      die Spalte. Leertaste legt sie ab.
- [ ] 6. Im Dialog lassen sich Titel, Beschreibung und Prioritaet aendern. Schliesst du
      ihn mit ungespeicherten Aenderungen, fragt die App nach.
- [ ] 7. Prioritaetsfilter und Wortfilter wirken gleichzeitig. Die Spaltenueberschriften
      bleiben sichtbar.
- [ ] 8. Nach dem Neuladen sind alle Karten in derselben Spalte und Reihenfolge.
- [ ] 9. Kaputte gespeicherte Daten zeigen ein leeres Board mit einer verstaendlichen
      Meldung. So testest du das: Browser-Entwicklertools oeffnen (F12), Reiter
      „Application“, Local Storage, den Wert durch `kaputt` ersetzen, Seite neu laden.
- [ ] 10. Deine drei Entscheidungen aus Schritt 1 funktionieren so, wie du sie
      beschrieben hast.

**Geht ein Punkt nicht,** schreib Claude eine Nachricht.

**Das muss Claude wissen:**

- Welcher Punkt nicht geht.
- Was du genau siehst.
- Dass zuerst ein Test den Fehler zeigen soll und erst danach repariert wird.

## 7. Optional: automatische Browser-Tests

Nur wenn noch Zeit ist.

**Ziel:** Automatische Browser-Tests fuer die Punkte unten laufen ohne Fehler.

**a) Vorlage holen.** Fuer Browser-Tests gibt es eine Vorlage. Hol sie jetzt, weil du
jetzt an dieses Problem kommst: `/ref playwright`.

**b) Tests schreiben lassen.** Eine normale Nachricht, kein Befehl.

**Das muss Claude wissen:**

- Dass es Playwright-Tests schreiben und ausfuehren soll.
- Welche Punkte getestet werden (Liste unten).
- Dass es die Playwright-Vorlage aus `.claude/references/INDEX.md` nutzen soll.
- Dass es gefundene Fehler behebt, aber keine neuen Funktionen baut.

Punkte:

1. Beim Tippen im Dialog bleibt der Cursor im richtigen Feld.
2. Jede Karte zeigt im Dialog ihre eigenen Werte, auch nach dem Wechsel zu einer anderen
   Karte.
3. Verschieben geht mit Tab, Leertaste und Pfeiltasten. Ein unsichtbarer Text fuer
   Screenreader meldet jeden Schritt.
4. Alle Knoepfe, Felder und der Dialog haben einen Namen fuer Screenreader.
5. Der Fokus bleibt im offenen Dialog und springt beim Schliessen zurueck zur Karte.
6. Beim Anlegen, Verschieben, Bearbeiten und Filtern erscheinen keine Fehler in der
   Browser-Konsole.

**Pruefe:**

- [ ] Claude meldet, dass alle Tests ohne Fehler durchlaufen.
- [ ] Du hast die App danach noch einmal selbst im Browser angeschaut.
