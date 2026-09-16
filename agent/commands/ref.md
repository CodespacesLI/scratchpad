---
description: Holt einzelne Eintraege der festen Referenzliste per Git lokal als Kopiervorlage
argument-hint: <slug ...> | all
risk: repeatable
cost: cheap
---

Lies `<AGENTENORDNER>/vorgehen/referenzen-holen.md` und folge ihr Schritt fuer Schritt.

Wozu: `/ref` laedt fertigen Code herunter und schreibt pro Datei den lokalen Pfad und eine
Erklaerung, wofuer sie die Vorlage ist, in `<AGENTENORDNER>/references/INDEX.md`. `/plan`
liest `INDEX.md` gleich zu Beginn und weiss so bei jedem Problem sofort, wo passender Code
liegt. Im echten Leben liest Claude die geholten Dateien selbst und schreibt die Erklaerung
selbst. In dieser Uebung gibt `referenzen.md` beides vor: welche Dateien geholt werden und
die Erklaerung dazu.

Eingabe: $ARGUMENTS (Slugs aus `<AGENTENORDNER>/references/referenzen.md`, `all` fuer
alle; leer heisst: Slugs mit Thema auflisten und nachfragen)

Der Schritt ist mechanisch: Git-Befehle ausfuehren, Pfade pruefen, Index fortschreiben.
Kannst du Arbeiter starten, gib ihn an einen Arbeiter auf dem guenstigen Modell im
Hintergrund und lass dir nur die Meldung aus Schritt 7 zurueckgeben, nicht die
Git-Ausgaben.

Du holst nur gelistete Quellen, suchst nichts im Netz und baust keinen Anwendungscode. Am
Ende nennst du die geholten Slugs, jeden fehlenden Pfad mit dem Wort `FEHLT` davor und
den Pfad zu `<AGENTENORDNER>/references/INDEX.md` und stoppst. Der Zeitpunkt
ist nach dem Brainstorm und vor `/plan`: geholt werden die Slugs, die der Brief nennt.
Danach geht es mit `/plan` weiter.
