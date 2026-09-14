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

## Überspringen

Stehen **wer** es nutzt, **was** er sieht und **was im Fehlerfall passiert** schon im
Prompt, wird nicht gefragt: dann direkt zum Brief und weiter zu Schritt 2.

## Abschluss — der Brief

```
## Brief: <Name>

**Zweck:**      <wessen Problem, wie oft, was heute stattdessen>
**Kern:**       <die eine Sache, die rein muss>
**Nicht-Ziel:** <was bewusst draussen bleibt (mindestens eins)>
**Ablauf:**     <was der User Schritt für Schritt sieht>
**Randfälle:**  <leer / Abbruch / abgelaufen / keine Rechte>
**Erfolg:**     <woran man bald sieht, dass es trägt>
```

Bei einem grösseren Vorhaben den Brief kurz bestätigen lassen, dann mit ihm als
geklärter Absicht an Schritt 2 (`<AGENTENORDNER>/vorgehen/02-plan.md`) übergeben.

**Grenze:** dieser Schritt fragt und verdichtet. Er plant nicht und baut nicht.
