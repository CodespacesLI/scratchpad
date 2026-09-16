---
description: Macht aus einem Brief einen freigabefertigen Plan mit kleinen Tasks
argument-hint: <Brief, Absicht oder Pfad zum Brief>
risk: repeatable
cost: expensive
---

Lies `<AGENTENORDNER>/vorgehen/02-plan.md` und folge ihr Schritt fuer Schritt.

Eingabe: $ARGUMENTS

Zu Beginn liest du `<AGENTENORDNER>/references/INDEX.md`. Dort steht der Code, den der
User vorher mit `/ref` geholt hat, pro Datei mit lokalem Pfad und Erklaerung. Jeder Task,
zu dem dort geholter Code passt, traegt im Feld „Vorlage:“ diesen lokalen Pfad.

Modus A gilt: du bist der Orchestrator. Die Codebase-Erkundung dispatchst du ueber das
Task-Werkzeug an einen Lese-Arbeiter, und den Gegenleser der Plan-Phase startest du als
eigenen Subagenten, nicht als Rollenwechsel im selben Kontext.

Modell: Entwurf und Gegenleser laufen beide auf dem teuren Modell — in dieser Phase
zaehlt Urteilskraft, und ein Denkfehler im Plan wird spaeter von jedem Arbeiter
mitgebaut. Der Gegenleser bekommt NUR den Entwurf, nie deinen Autor-Kontext. Begruendung:
`<AGENTENORDNER>/vorgehen/rollen.md`, Abschnitt „Welches Modell für welche Rolle".

Kannst du keine Subagenten starten, gilt Modus B: du erkundest selbst (gezielt, nur
die Fundstellen notieren) und liest den Entwurf als bewusster Rollenwechsel gegen.
Sag dem User in einem Satz, dass der Gegenleser dann kein echter Zweitleser ist.

Der Plan wird als `<AGENTENORDNER>/tasks/<slug>.md` angelegt (fertige Plaene wandern
spaeter nach `<AGENTENORDNER>/tasks/done/` und werden nie geloescht). Jeder Task traegt
1–3 testbare Kriterien im Muster „Wenn <Ausloeser>, dann <Ergebnis>" — ohne sie ist beim
Bauen nicht entscheidbar, ob er fertig ist.

Am Ende legst du dem User den Plan zur Freigabe vor und stoppst.
