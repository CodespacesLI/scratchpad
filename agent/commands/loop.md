---
description: Schaerft den aktuellen Unterschied nach: Review und Fix im Wechsel, bis zwei saubere Runden in Folge
argument-hint: <optionaler Umfang, z.B. ein Pfad; leer = der gesamte aktuelle Unterschied>
risk: destructive
cost: expensive
---

Eine Konvergenz-Schleife über den aktuellen Unterschied (`git diff`, ungestaged und
gestaged). `$ARGUMENTS` grenzt den Umfang ein (Pfad oder Unterordner); leer heisst alles.

Die Entscheidung, wann eine Schleife statt eines Dispatchs richtig ist, steht in
`<AGENTENORDNER>/vorgehen/03-build.md`, Abschnitt „Vorfrage — Schleife oder Arbeiter?".

## Eine Runde

1. **Review-Arbeiter** (teures Modell, eigener Subagent, frischer Kontext): bekommt den
   aktuellen Unterschied und den Auftrag, Mängel zu finden — fehlende Tests, ungedeckte
   Fehlerfälle, Verstösse gegen die Projektregeln, Duplikate zu Bestehendem, tote Pfade.
   Rückgabe: nummerierte Befunde, je mit `Pfad:Zeile`, Schweregrad und einem Satz
   Begründung — oder das Wort **SAUBER**.
2. **Fix-Arbeiter** (eigener Subagent): behebt die Befunde **test-first** — erst der
   Test, der den Mangel nachstellt und **rot** läuft, dann der Fix bis grün. Der
   Rot-Beleg gehört in seine Rückgabe.
3. **Zustand fortschreiben**, dann nächste Runde gegen den **neu berechneten**
   Unterschied.

**Jede Runde ist ein frischer Dispatch.** Keine Runde setzt den Arbeiter der Vorrunde
fort — Review und Fix laufen jede Runde als neu gestartete Subagenten, im **Hintergrund**
statt synchron, damit der laufende Zug nicht an ihnen hängt und ein Abbruch im Gespräch
ihre Arbeit nicht mitreisst. Gefixt wird über **einen** Fix-Arbeiter nacheinander, nie
über mehrere parallele Fixer auf demselben Code: zwei Fixer in derselben Datei
überschreiben sich gegenseitig, und die nächste Review-Runde misst dann eine Fassung,
die so niemand gebaut hat.

**Über ~120k Tokens hinaus bekommt kein Arbeiter Folgearbeit.** Er schliesst am nächsten
natürlichen Übergabepunkt ab, gibt einen kompakten Stand-Brief zurück, und die Restarbeit
geht an einen frischen Arbeiter; reine Test- oder Build-Ausläufe dürfen auslaufen.

**Keine Zwischenfragen an den User.** Alles, was Entscheidung ist, wird geparkt und erst
am Ende gebündelt vorgelegt.

## Fertig-Kriterium

- Eine Runde gilt als **sauber**, wenn der Review-Arbeiter **null neue Befunde** meldet.
- Fertig ist die Schleife nach **zwei sauberen Runden IN FOLGE**. Auch wenn Runde 1
  schon sauber ist, läuft Runde 2 — sonst ist es keine Bestätigung, sondern Zufall.
  Ein Befund in Runde 3 setzt die Serie auf null zurück.
- **Obergrenze: 6 Runden.** Danach wird abgebrochen und berichtet, was offen blieb.
  Mehr Runden kaufen kaum noch Befunde für viel Geld.

## Zustand — in der Datei, nicht im Gespräch

Nach jeder Runde nach `<AGENTENORDNER>/state/loop-stand.md` schreiben:
Rundenzähler, aktuelle Serie sauberer Runden, je Befund ein Fingerabdruck
(`Pfad:Zeile` + Kern der Aussage in fünf Worten), geparkte Streitfälle.

Das ist nicht Buchhaltung, sondern der Grund, warum die Schleife billig bleibt: **jede
Runde startet mit frischem Kontext und liest den Stand aus der Datei**, statt den
Verlauf aller Vorrunden mitzuschleppen.

## Pendel-Regel

Wird **dieselbe Stelle zum zweiten Mal gegensätzlich „repariert"** — Runde 2 baut zurück,
was Runde 1 gebaut hat —, ist das kein Mangel mehr, sondern ein Streitfall ohne
eindeutige Antwort.

Dann: **sofort abbrechen**, den Stand so lassen, wie er ist, den Fall in
`loop-stand.md` unter „geparkt" festhalten und dem User vorlegen — mit **beiden**
Positionen und je einem Satz, was für sie spricht. Nicht selbst entscheiden, nicht
weiterpendeln.

## Abschluss

Bericht nach `<AGENTENORDNER>/vorgehen/antwortform.md`, im Flow und in höchstens fünf
Zeilen: wie viele Runden, was behoben wurde, womit die Schleife endete (zwei saubere
Runden / Obergrenze / Pendel-Abbruch). Keine Aufzählung der einzelnen Befunde, keine
Schluss-Zusammenfassung. Danach alle geparkten Streitfälle an **einem** Gate, in
Produktsprache übersetzt — die `Pfad:Zeile`-Belege bleiben intern, bis der User
ausdrücklich danach fragt. Nicht gekürzt wird, was schiefging: rote Tests, abgebrochene
Runden, offen Gebliebenes stehen im Bericht, auch wenn es ihn länger macht.
