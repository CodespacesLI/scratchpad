# Übung: ein Task-Board bauen, einmal durch das ganze Harness

Grüne Wiese. Es gibt keinen Startcode. Dieses Blatt ist der Auftrag, `referenzen.md`
daneben ist die Sammlung fremder Repos, in denen du während der Arbeit nachschlägst.

**Stack, nicht verhandelbar:** Vite, React, TypeScript. Vitest für Logik- und
Unit-Tests, Playwright für End-to-End. Kein Backend, keine API-Schlüssel, keine Cloud,
kein Docker. Der Stand liegt lokal im Browser.

---

## 1. Was am Ende dasteht

Jemand öffnet die Seite und sieht sein Board: drei Spalten nebeneinander, in den Spalten
Karten mit je einem Titel. Er zieht eine Karte von links nach rechts, wenn er mit ihr
weitergekommen ist. Er klickt eine Karte an und bekommt einen Dialog, in dem Titel,
Beschreibung und Priorität stehen und in dem er sie ändern kann. Über dem Board sitzt
ein Filter, mit dem er nur die Karten sieht, die ihn gerade interessieren. Ist eine
Spalte leer, steht dort ein Satz, der sagt was zu tun ist, und nicht einfach nichts.

Beim nächsten Öffnen ist alles noch da.

Wer keine Maus benutzen will oder kann, kommt mit der Tastatur genauso durch: Karte
anwählen, verschieben, ablegen, ohne zu ziehen.

## 2. Der Auftrag

Du baust dieses Board für einen einzelnen Menschen, der seine eigene Arbeit sortiert.
Kein Team, keine Freigaben, keine Zuweisung an andere.

**Die Spalten** heissen zunächst Offen, In Arbeit, Fertig. Eine Karte trägt Titel,
optionale Beschreibung, eine Priorität und die Spalte, in der sie steht. Neue Karten
entstehen direkt in einer Spalte.

**Das Verschieben** ist der Kern. Mit der Maus gezogen, mit der Tastatur bedient, und in
beiden Fällen sieht der Nutzer vorher, in welcher Spalte die Karte landen wird.

**Der Detail-Dialog** öffnet sich über einer Karte, zeigt ihre Felder zum Bearbeiten und
schliesst wieder. Was der Nutzer währenddessen getippt hat, darf beim Schliessen nicht
verschwinden, ohne dass er es gewollt hat.

**Der Filter** über dem Board schränkt ein, was sichtbar ist: nach Priorität, nach einem
Wort im Titel, oder beides.

Drei Dinge sagt der Nutzer über seine Arbeitsweise, und sie stehen hier so, wie er sie
gesagt hat:

> „Ich fange zu viel gleichzeitig an. Das Board soll mir das zeigen, wenn die mittlere
> Spalte zu voll wird."

> „Wenn ich nach hoher Priorität filtere und dann eine Karte umsortiere, will ich
> nachher nicht feststellen, dass die anderen Karten durcheinander sind."

> „Ich habe das oft in zwei Fenstern nebeneinander offen, links das Board, rechts meine
> Notizen. Manchmal auch zweimal das Board."

Diese drei Sätze sind der Grund, warum die Übung mit `/brainstorm` anfängt und nicht mit
`/plan`. Sie beschreiben Wünsche, keine Lösungen, und mindestens zwei davon lassen sich
nicht gleichzeitig maximal erfüllen. Welche Seite gewinnt, entscheidest du im Brief,
begründet, und danach hältst du dich daran.

## 3. Nicht-Ziele

Damit die Übung in der Zeit bleibt, bleibt das hier draussen, ausdrücklich und ohne
Diskussion:

- Kein Login, keine Benutzer, keine Rollen, keine Mandanten.
- Kein Server, keine API, keine Synchronisation über Geräte hinweg.
- Kein Anlegen, Umbenennen oder Löschen von Spalten. Drei feste Spalten genügen.
- Keine Anhänge, keine Bilder, keine Kommentare, keine Checklisten in der Karte.
- Keine Fälligkeitsdaten, keine Erinnerungen, keine Kalenderansicht.
- Keine Swimlanes, keine Unterboards, keine Labels ausser der einen Priorität.
- Kein Dark Mode, kein Theming, keine eigene Mobilansicht.
- Kein Sortieren innerhalb einer Spalte. Eine Karte wechselt die Spalte und hängt sich
  dort unten an; eine Reihenfolge von Hand gibt es nicht.
- Kein Abgleich zwischen zwei gleichzeitig offenen Fenstern. Was du zum dritten
  zitierten Satz entscheidest, steht im Brief; gebaut wird höchstens, dass das zweite
  Fenster beim nächsten Öffnen den zuletzt geschriebenen Stand sieht.
- Keine Undo-Historie über das Neuladen hinaus.
- Kein Deployment, keine CI-Pipeline, kein Docker.

Kommt eine dieser Ideen im Brainstorm hoch, wird sie als Nicht-Ziel notiert, nicht
diskutiert.

## 4. Der Weg durch das Harness

Sieben Stationen. Jede hat ein Ergebnis, an dem du siehst, dass sie fertig ist.

### Station 1: `/brainstorm`

```
/brainstorm ein Task-Board fuer meine eigene Arbeit, drei Spalten, Karten ziehen
```

Die KI baut nichts. Sie fragt in Runden, zwei bis vier Fragen pro Runde. Erwarte, dass
sie genau an den drei zitierten Sätzen aus Abschnitt 2 bohrt: Was heisst „zu voll",
anzeigen oder blockieren? Was ist beim Filter die wahre Reihenfolge? Was passiert beim
zweiten Fenster? Weich nicht aus. Eine schwammige Antwort führt zu einer schwammigen
Akzeptanz und die merkst du erst beim Testen.

**Fertig, wenn** der Brief aus sechs Zeilen dasteht (Zweck, Kern, Nicht-Ziel, Ablauf,
Randfälle, Erfolg) und du ihn bestätigt hast. Kein Code, keine Datei.

### Station 2: `/plan`

```
/plan
```

Die KI erkundet erst, was schon da ist. Auf grüner Wiese ist das kurz, und das ist der
Moment, in dem `referenzen.md` zählt: die fremden Repos sind deine Erkundung. Dann
schreibt sie einen Entwurf und gibt ihn an einen zweiten Arbeiter mit frischem Kontext,
der ihn zerreissen soll.

Schau dir die Einwände des Gegenlesers wirklich an, bevor du freigibst. Erfahrungsgemäss
findet er nicht den zu grossen Entwurf, sondern den zu kleinen: fehlender Leerzustand,
fehlender Fehlerzustand, Tastaturbedienung nur angedeutet.

**Fertig, wenn** `.claude/tasks/board.md` mit `Status: entwurf` liegt, jeder Task 2 bis 5
Minuten Arbeit ist und 1 bis 3 Kriterien im Muster „Wenn X, dann Y" trägt, und du
freigegeben hast.

### Station 3: `/build`, erste Welle

```
/build .claude/tasks/board.md
```

Der Plan geht auf `Status: im-bau`. Die KI baut nicht selbst, sie verteilt. Jeder
Arbeiter bekommt einen Task, seine Dateiliste und die Ansage: erst der Test, einmal rot,
dann bauen bis grün. Im selben Auftrag stehen das harte Limit von höchstens 30
Werkzeug-Aufrufen, das Budget von rund 120 000 Tokens und, bei längeren Aufträgen, der
Pfad der Mitschreib-Datei unter `.claude/state/`. Fehlt eine dieser Angaben, läuft der
Arbeiter ins Uferlose.

Halt diese Welle bewusst bei dem an, was ohne Drag-and-Drop läuft: Board, Spalten,
Karten anlegen, Detail-Dialog, Persistenz, Leerzustand. Das ist der erste Punkt, an dem
du etwas im Browser siehst. Mach `npm run dev` auf und sieh es dir an, bevor du
weitergehst.

**Fertig, wenn** die Tasks dieser Welle abgehakt sind, die Vitest-Suite grün ist und das
Board im Browser steht.

### Station 4: `/handoff`, `/clear`, `/resume`

Das ist der Teil der Übung, den man nicht überspringt, auch wenn der Kontext noch nicht
voll ist. Hier lernst du die Mechanik, damit du sie später kennst, wenn es weh tut.

```
/handoff
```

Die KI schreibt den Stand nach `.claude/state/handoff-brief.md`. **Mach die Datei auf und
lies sie.** Eine Seite, vier Abschnitte: ERLEDIGT, OFFEN, WO ICH STEHE, BELEGE UND
STOLPERSTEINE. Keine Diffs, keine Code-Blöcke, keine Nacherzählung. Steht dort etwas
Falsches, ist das jetzt sichtbar und nicht erst in zwanzig Minuten.

```
/clear
```

Das tippst du selbst. Kein Command und kein Wächter kann das Gespräch leeren, einen
automatischen Rollover gibt es in diesem Harness nicht. Das ist Handarbeit, und es ist
wichtig, dass du weisst warum: ein Hook kann einen Zug beenden und eine Auflage
mitgeben, mehr nicht.

```
/resume
```

Im leeren Gespräch. Achte darauf, was jetzt passiert: die KI liest den Brief und prüft
ihn gegen den Arbeitsbaum, statt ihm zu glauben. Branch, letzter Commit, Abhak-Stand im
Plan, zwei Stichproben aus ERLEDIGT. Wenn du zwischendurch heimlich einen Task von Hand
abhakst, siehst du den Mechanismus arbeiten.

**Fertig, wenn** die neue Sitzung von sich aus sagt, wo sie weitermacht, und der Stand
stimmt.

### Station 5: `/build`, zweite Welle

Dieselbe Plandatei, im frischen Kontext. Jetzt kommt das Schwierige: Drag-and-Drop mit
der Maus, dieselbe Bewegung mit der Tastatur, der Filter, und die Entscheidung aus dem
Brainstorm zur vollen Spalte.

Hier wird sich zeigen, ob dein Plan die Tastaturbedienung als eigenen Task geschnitten
hat oder als Nebensatz an den Drag-and-Drop-Task gehängt. Der Nebensatz wird nicht
gebaut. Das ist die Lehre.

**Fertig, wenn** alle Tasks abgehakt oder begründet gestrichen sind, der Plan auf
`Status: fertig` steht und nach `.claude/tasks/done/` gewandert ist.

### Station 6: `/loop`

```
/loop
```

Review-Arbeiter findet Mängel, Fix-Arbeiter behebt sie test-first, nächste Runde gegen
den neu berechneten Unterschied. Fertig nach zwei sauberen Runden in Folge.

Schau während der Runden in `.claude/state/loop-stand.md`. Dort steht der Zustand, nicht
im Gespräch, und genau deshalb wächst der Kontext über die Runden nicht mit.

**Fertig, wenn** zwei saubere Runden hintereinander gemeldet sind, oder die Schleife
wegen der Pendel-Regel abbricht und dir einen Streitfall vorlegt. Beides ist ein
gültiges Ende.

### Station 7: Abnahme im Browser

Playwright gegen die Kriterien aus den Abschnitten 5 und 6. Dann selbst durchklicken.
Ein grüner Testlauf ohne einen einzigen Blick auf die echte Oberfläche ist keine
Abnahme.

## 5. Abnahmekriterien

Testbar, im Format aus `kern/task-format.md` (im installierten Projekt liegt dieselbe
Datei unter `.claude/vorgehen/task-format.md`). Das hier ist die Untergrenze. Was du im
Brainstorm zu den drei zitierten Sätzen entschieden hast, kommt als eigener Satz in
derselben Form dazu, sonst ist die Entscheidung nicht überprüfbar.

1. Wenn das Board zum ersten Mal geöffnet wird, dann stehen drei Spalten mit den Titeln
   Offen, In Arbeit und Fertig nebeneinander.
2. Wenn eine Spalte keine Karte enthält, dann zeigt sie einen Leerzustand mit einem Satz
   und einer Möglichkeit, dort eine Karte anzulegen.
3. Wenn der Nutzer in einer Spalte eine neue Karte mit dem Titel „Kaffee kaufen" anlegt,
   dann erscheint diese Karte als unterste Karte genau dieser Spalte.
4. Wenn der Nutzer eine Karte mit der Maus in eine andere Spalte zieht und dort loslässt,
   dann steht sie als unterste Karte der Zielspalte.
5. Wenn eine gezogene Karte über einer anderen Spalte schwebt und noch nicht losgelassen
   ist, dann ist diese Spalte sichtbar als Ziel hervorgehoben.
6. Wenn eine Karte den Tastaturfokus hat und der Nutzer die Leertaste drückt, dann
   wechselt die Karte in einen Verschiebemodus, der als Text angesagt wird.
7. Wenn sich eine Karte im Verschiebemodus befindet und der Nutzer die Pfeiltaste nach
   rechts drückt, dann wandert sie in die nächste Spalte.
8. Wenn sich eine Karte im Verschiebemodus befindet und der Nutzer die Leertaste drückt,
   dann wird sie in der Spalte abgelegt, in der sie gerade steht, und der Verschiebemodus
   endet.
9. Wenn der Nutzer eine Karte anklickt, dann öffnet sich ein Dialog mit Titel,
   Beschreibung und Priorität dieser Karte in bearbeitbaren Feldern.
10. Wenn der Nutzer im Dialog den Titel ändert und speichert, dann zeigt die Karte auf
    dem Board sofort den neuen Titel, ohne dass die Seite neu geladen wird.
11. Wenn der Nutzer im Dialog etwas geändert hat und den Dialog über Escape schliesst,
    dann wird er auf den drohenden Verlust hingewiesen, bevor der Dialog verschwindet.
12. Wenn der Filter auf Priorität „hoch" gestellt wird, dann sind ausschliesslich Karten
    mit dieser Priorität sichtbar, und jede Spalte zeigt weiterhin ihre Überschrift.
13. Wenn der Filter ein Wort enthält, zu dem keine Karte passt, dann erscheint ein
    Leerzustand, der den Filter benennt und ihn zurücksetzen lässt.
14. Wenn der Nutzer die Seite neu lädt, dann stehen alle Karten in derselben Spalte und
    in derselben Reihenfolge wie vor dem Neuladen.
15. Wenn der gespeicherte Stand nicht gelesen werden kann, dann startet das Board mit
    einem leeren Zustand und zeigt eine verständliche Meldung, statt weiss zu bleiben.

## 6. Qualitätskriterien für die Oberfläche

Aus dem QA-Katalog, auf dieses Board angewendet. Jeder Punkt ist so formuliert, dass er
sich als Playwright-Spec schreiben lässt. Wo eine Spec allein nicht reicht, steht es
dabei.

**Fokus hält beim Tippen.** Wenn der Nutzer im Detail-Dialog zehn Zeichen in das
Titelfeld tippt, dann liegt der Fokus nach dem zehnten Zeichen noch auf demselben Feld
und der Cursor steht hinter dem zehnten Zeichen, nicht am Anfang. Spec: Zeichen einzeln
tippen, nach jedem Anschlag das fokussierte Element und die Cursorposition prüfen.

**Kartenzustand überlebt den Dialogwechsel.** Wenn der Nutzer den Dialog von Karte A
schliesst, den von Karte B öffnet und wieder zu Karte A zurückkehrt, dann zeigt A
unverändert ihre eigenen Werte und keine Reste von B.

**Drag-and-Drop ist per Tastatur bedienbar.** Wenn der Nutzer ausschliesslich Tab,
Leertaste und Pfeiltasten benutzt, dann bringt er jede Karte in jede Spalte, und jeder
Schritt wird über einen ARIA-Live-Bereich als Text ausgegeben. Spec: kein `mouse.move`,
kein `dragTo`, nur `keyboard.press`, und am Ende die Spaltenzuordnung im DOM prüfen.

**Leerzustand und Fehlerzustand existieren.** Wenn eine Spalte leer ist, dann steht dort
sichtbarer Text. Wenn der lokal gespeicherte Stand beschädigt ist, dann steht eine
Fehlermeldung ohne technische Kennung und ohne Stacktrace. Spec: den Speicher vor dem
Seitenaufruf mit Müll füllen, dann die Meldung prüfen.

**Jedes bedienbare Element hat einen zugänglichen Namen.** Wenn die Seite geladen ist,
dann trägt jeder Button, jedes Eingabefeld und jede ziehbare Karte einen zugänglichen
Namen, und der Dialog trägt einen eigenen. Spec: über die Accessibility-Baum-Abfrage
alle bedienbaren Rollen einsammeln und auf leeren Namen prüfen.

**Der Dialog fängt den Fokus und gibt ihn zurück.** Wenn der Dialog offen ist, dann
bleibt Tab innerhalb des Dialogs. Wenn er schliesst, dann liegt der Fokus wieder auf der
Karte, aus der er geöffnet wurde.

**Keine Fehler in der Konsole.** Wenn der Nutzer eine Karte anlegt, verschiebt, öffnet,
ändert und filtert, dann steht am Ende nichts in der Browser-Konsole. Insbesondere keine
Warnung über ein Feld, das von unkontrolliert auf kontrolliert wechselt.

## 7. Zeitbudget

Vier Stunden netto. Die Aufteilung ist eine Erwartung, keine Stoppuhr.

| Station | Minuten | Woran du merkst, dass du zu lange brauchst |
|---|---|---|
| Brainstorm | 20 | Ihr diskutiert Technik statt Nutzen. |
| Plan und Gegenleser | 30 | Tasks werden grösser als fünf Minuten Arbeit. |
| Build, erste Welle | 50 | Du liest Arbeiter-Ausgaben statt Rückgaben. |
| Handoff, Clear, Resume | 15 | Der Brief ist länger als eine Seite. |
| Build, zweite Welle | 60 | Die Tastaturbedienung hängt an einem anderen Task. |
| Loop | 25 | Die Schleife pendelt, statt zu konvergieren. |
| Abnahme im Browser | 40 | Du schreibst neue Features statt Specs. |

Bleibt Zeit übrig, geht sie in Station 7, nicht in ein weiteres Feature. Die Nicht-Ziele
aus Abschnitt 3 bleiben auch dann Nicht-Ziele.
