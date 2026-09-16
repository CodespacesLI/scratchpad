# Schritt 1 — Brainstorm: die Absicht klären

**Zweck:** sicherstellen, dass das **richtige** Problem gelöst wird, bevor jemand plant
oder baut. Die Plan-Phase zerlegt später den technischen Weg. Die Absicht prüft sonst
niemand.

## Grundhaltung

- **Eine schwammige Antwort ist keine Antwort.** „Für alle", „so wie X, nur besser",
  „mal schauen" → zurückweisen und konkret nachfragen.
- **Jede Annahme ist eine Entscheidung.** Setzt jemand etwas als selbstverständlich
  („natürlich als Web-Seite", „klar mit Login"), frag: warum das und nicht die
  Alternative?
- **Verteidige den Nutzer, nicht die Idee.** Deine Aufgabe ist, die schwächste Stelle zu
  finden, solange sie noch nichts kostet.
- **Fragen nummerieren**, damit der User gezielt „zu 3:" antworten kann.
- **In Runden fragen, nicht als Fragen-Wand:** 2–4 scharfe Fragen pro Runde, auf die
  Antworten eingehen, nachhaken wo ausgewichen wird, erst dann die nächste Runde.
- Sprache: Alltagsworte, kein Fachjargon, kein Code in den Fragen.

## Runde 1 — Zweck und Schmerz

- Wessen Problem ist das, und wie oft tritt es auf? Eine konkrete Person oder Situation.
- Was macht diese Person heute stattdessen: ein anderes Werkzeug, eine Liste, gar
  nichts? Bei „gar nichts": ist der Schmerz dann gross genug?
- Gibt es das schon? Wenn ja, warum bauen statt nutzen? Wenn nein, warum wohl nicht?

## Runde 2 — Umfang kleinrechnen

- Was ist die **eine** Sache, die drin sein muss, damit es überhaupt Wert hat?
- Streich-Test: nenne 2–3 Dinge, die der User vermutlich „auch noch" will, und frag je
  einzeln, ob sie im ersten Wurf wirklich rein müssen.
- Erzwinge mindestens ein echtes Nicht-Ziel. Ohne Grenze ist der Umfang nicht
  geschnitten.

## Runde 3 — nur wenn nötig

- Was sieht der User Schritt für Schritt?
- Randfälle: leere Daten, Abbruch mittendrin, abgelaufen, fehlende Rechte.
- Zielkonflikte: schnell gegen gründlich, einfach gegen flexibel. Welche Seite gewinnt
  im Zweifel, und warum?

## Pflichtfrage — fertigen Code nutzen

Diese Frage stellst du in jedem Brainstorm, spätestens in der letzten Runde vor dem Brief:

- Für welche Teile gibt es schon fertigen, getesteten Code (Open Source), den wir nutzen,
  statt ihn neu zu erfinden? Nenne dazu die Teile, die du für schwierig hältst.

In der Übung ist die Auswahl fest: `<AGENTENORDNER>/references/referenzen.md` nennt pro
Problem einen Slug. Der User antwortet mit Slugs aus dieser Liste, zu jedem schwierigen
Teil den passenden. Du schlägst keine Quelle ausserhalb der Liste vor und holst in diesem
Schritt noch nichts.

## Überspringen

Stehen **wer** es nutzt, **was** er sieht und **was im Fehlerfall passiert** schon im
Prompt, fallen die Runden weg. Die Pflichtfrage nach fertigem Code stellst du trotzdem,
es sei denn, der Prompt nennt die Slugs schon. Dann direkt zum Brief.

## Abschluss — der Brief

```
## Brief: <Name>

**Zweck:**      <wessen Problem, wie oft, was heute stattdessen>
**Kern:**       <die eine Sache, die rein muss>
**Nicht-Ziel:** <was bewusst draussen bleibt (mindestens eins)>
**Ablauf:**     <was der User Schritt für Schritt sieht>
**Randfälle:**  <leer / Abbruch / abgelaufen / keine Rechte>
**Erfolg:**     <woran man bald sieht, dass es trägt>
**Vorlagen:**   <je gewählter Slug eine Zeile: `<slug>` — welches Problem er löst; oder „keine“>
```

Bei einem grösseren Vorhaben den Brief kurz bestätigen lassen. Nennt der Brief Vorlagen,
sagst du dem User zum Abschluss, dass er genau diese Slugs **jetzt, vor dem Plan** holt:
`/ref <slug ...>` (in Codex: `Referenzen: <slug ...>`), Ablauf in
`<AGENTENORDNER>/vorgehen/referenzen-holen.md`. Danach geht der Brief als geklärte Absicht
an Schritt 2 (`<AGENTENORDNER>/vorgehen/02-plan.md`), der den Index der geholten Vorlagen
liest.

**Grenze:** dieser Schritt fragt und verdichtet. Er holt nichts, plant nicht und baut
nicht.
