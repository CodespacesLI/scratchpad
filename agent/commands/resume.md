---
description: Nimmt die Arbeit nach /handoff und /clear wieder auf: Brief lesen, gegen den Arbeitsbaum pruefen, weitermachen; stand der Vorgaenger im Bau, den ersten offenen Task nennen und an /build weiterleiten
argument-hint: <optionale Kurskorrektur, z.B. "mach mit Task 3 weiter"; leer = dem Brief folgen>
risk: repeatable
cost: cheap
---

Nimmt die Arbeit im frischen Gespräch wieder auf: liest
`<AGENTENORDNER>/state/handoff-brief.md`, **prüft ihn gegen den echten Arbeitsbaum** und
macht beim ersten offenen Punkt weiter. Stand der Vorgänger im Plan-Abbau, baut `/resume`
nicht selbst, sondern nennt den ersten offenen Task und leitet an `/build` weiter
(Schritt 4). Hintergrund: `<AGENTENORDNER>/vorgehen/04-kontext.md`.

`$ARGUMENTS` ist eine optionale Kurskorrektur des Users; leer heisst dem Brief folgen.

## Schritt 1 — Brief lesen

`<AGENTENORDNER>/state/handoff-brief.md`.

Liegt dort keiner: **eine** Zeile ausgeben und stoppen. Nichts raten, nichts
rekonstruieren, keinen Suchlauf starten.

> Kein Handoff-Brief unter `<AGENTENORDNER>/state/handoff-brief.md` — sag mir, woran ich
> weiterarbeiten soll, oder lass den vorigen Kontext `/handoff` laufen.

## Schritt 2 — Prüfen, nicht glauben

**Der Brief ist ein Bericht, kein Beweis.** Zwischen Schreiben und Lesen kann der User
selbst committet, den Branch gewechselt oder etwas verworfen haben. Deshalb wird **jeder
Kernpunkt** einmal gegengeprüft — billig, gezielt, ohne Erkundungslauf:

1. **Branch und letzter Commit:** `git status --short`, `git log --oneline -3`. Weicht
   etwas vom Kopf des Briefs ab, ist der Brief mindestens teilweise veraltet.
2. **Der Plan:** die im Brief genannte Datei unter `<AGENTENORDNER>/tasks/` öffnen und nur die
   Task-Liste gegen ERLEDIGT und OFFEN halten. **Bei Widerspruch gewinnt der Plan**, denn
   er wird beim Abhaken mitgeschrieben, der Brief nur einmal.
3. **Je ein Stichprobe-Beleg aus ERLEDIGT:** existiert die genannte Datei, steht die
   genannte Zeile dort wirklich? Zwei bis drei Stichproben genügen, keine Vollprüfung.

**Bei Widerspruch gewinnt immer der Arbeitsbaum.**

## Schritt 3 — Abweichungen benennen

Weicht etwas ab, wird es dem User in **einer bis drei Zeilen** gesagt, bevor gearbeitet
wird — kein stilles Überschreiben und keine stille Anpassung:

> Der Brief sagt, Task 4 sei offen; im Plan ist er abgehakt und der Commit dazu liegt
> vor. Ich mache bei Task 5 weiter.

Passt alles, reicht ein Satz: „Brief geprüft, Stand passt — ich mache bei X weiter."

## Schritt 4 — Weitermachen

Beim ersten offenen Punkt aus OFFEN anfangen (oder bei dem, den `$ARGUMENTS` nennt) und
in dem Vorgehen weiterarbeiten, in dem der Vorgänger stand:

- **Plan-Abbau (der Vorgänger stand in `/build`):** `/resume` startet selbst keine
  Arbeiter. Nenne den ersten offenen Task des Plans und schliesse mit genau diesem Hinweis:
  „Weiter mit `/build <Pfad zum Plan>`." Der neue `/build` macht beim ersten offenen Task
  weiter und baut alle offenen Tasks am Stück (`<AGENTENORDNER>/vorgehen/03-build.md`,
  „Am Stück bis zum Ende"). So läuft nie ein zweiter Bau parallel zum ersten.
- **Nachschärfen:** weiter mit `/loop`.
- **Alles andere:** direkt beim ersten offenen Punkt weiterarbeiten.

Der Brief wird dabei **nicht** fortgeschrieben — er ist ein Schnappschuss. Wird der neue
Kontext wieder gross, schreibt der nächste `/handoff` ihn neu.
