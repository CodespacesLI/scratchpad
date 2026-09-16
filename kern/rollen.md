# Rollen und der kollisionsfreie Schnitt

Es gibt genau drei Rollen: **backend**, **frontend**, **fullstack**. Jeder Task im Plan
trägt eine davon.

Keine eigene Datenbank-Rolle: Schema und Migrationen sind Backend-Arbeit. Eine vierte
Rolle würde die Schnitt-Regeln verkomplizieren, ohne Parallelität zu gewinnen, denn
Schema-Änderungen dürfen ohnehin nie parallel zu etwas anderem laufen. Stattdessen gilt:
**Schema-Tasks bilden immer eine eigene, erste Welle, allein.**

`fullstack` ist **kein** dritter paralleler Arbeiter neben Backend und Frontend: das
wäre die Kollision in Person. Es ist das Solo-Playbook für die kleine End-zu-End-Änderung
(ein Endpunkt plus ein Feld in der Oberfläche), bei der Aufteilen mehr kostet, als es
bringt. Im parallelen Bau schneidet der Orchestrator immer in Backend- und
Frontend-Tasks.

## Der Schnitt — vier Regeln für den Orchestrator

1. **Disjunkt-Prüfung vor jeder Welle.** Vergleiche die `Files:`-Listen aller Tasks, die
   gleichzeitig laufen sollen, paarweise. Kommt ein Pfad zweimal vor, laufen die Tasks
   nicht parallel: entweder nacheinander, oder zu einem Task verschmelzen. Diese Prüfung
   ist die eigentliche Kollisionsvermeidung: ein Abgleich, keine Hoffnung.
2. **Vertrag zuerst.** Berührt ein Feature Backend und Frontend, ist der erste Task die
   Schnittstellen-Definition: Endpunkt-Signatur, Datenform, Beispiel-Antwort. Allein, vor
   jeder Parallelität. Danach baut Backend gegen den Vertrag und Frontend gegen den
   Vertrag (mit einer festen Beispiel-Antwort als Platzhalter), beide unabhängig
   voneinander.
3. **Wellen.** Welle 1 ist Schema und Vertrag, allein. Welle 2 und folgende bestehen aus
   Tasks ohne offene Abhängigkeit und mit disjunkten Files, typisch ein Backend- und ein
   Frontend-Arbeiter gleichzeitig. Die Verdrahtung (Integration, durchgehender Pfad) ist
   die letzte Welle, wieder allein.
4. **Datei-Zaun im Arbeiter.** Jeder Auftrag trägt den Satz: „Du änderst NUR die Dateien
   aus deiner Files-Liste. Brauchst du eine fremde Datei, änderst du sie NICHT, sondern
   meldest es unter OFFEN." Gemeinsame Dateien (Textkataloge, Sammel-Exporte,
   Routen-Registrierung) sind bekannte Kollisionsherde. Sie gehören dem Integrations-Task
   der letzten Welle, nie zwei parallelen Arbeitern.

## backend

**Deckt ab:** Datenmodell und Migrationen, Domänen- und Dienst-Logik, Endpunkte und deren
Tests.

**Ablauf:** Task und Akzeptanzkriterien lesen → Test schreiben und **rot** laufen lassen
(Ausgabe festhalten) → implementieren bis grün → gezielter Testlauf nur dieser Datei →
Rückgabe-Schema.

**Merksätze:** Die Rechteprüfung gehört in die Dienst-Schicht, nicht in die
Schnittstellen-Schicht. Keine Geschäftslogik im Endpunkt. Fehlerfälle sind Teil des
Tasks, nicht Kür.

## frontend

**Deckt ab:** Komponenten, Ansichten, Datenabruf im Client und deren Tests.

**Ablauf:** derselbe Rot-Grün-Zyklus wie oben.

**Merksätze:** Zuerst nach einer bestehenden Komponente suchen und sie erweitern, statt
eine zweite ähnliche zu bauen. Leer-, Lade- und Fehlerzustand gehören zu jeder Ansicht.
Sichtbare Texte kommen aus der Textdatei des Projekts, nie hartkodiert und nie geraten.

## fullstack

**Deckt ab:** den kleinen End-zu-End-Schnitt solo, in dieser Reihenfolge: Vertrag →
Backend → Frontend → Verdrahtung, jeder Schritt test-first.

**Zu-gross-Regel:** Werden daraus mehr als etwa drei Tasks, baue den abgrenzbaren Teil
fertig und melde unter OFFEN, dass der Task zu gross geschnitten ist. Der Orchestrator
legt das am Schluss-Gate vor; dann wird neu geschnitten und parallel gebaut.

Diese drei Playbooks sind keine Commands, sondern Text im Auftrag: der Orchestrator
schreibt das passende in den Arbeiter-Auftrag hinein. In Modus B sind es Rollen, die
derselbe Chat nacheinander einnimmt. Alle drei enden mit dem Datei-Zaun-Satz und dem
Rückgabe-Schema aus `<AGENTENORDNER>/vorgehen/rueckgabe-schema.md`.

## Welches Modell für welche Rolle

Rolle sagt, **was** ein Arbeiter tut. Genauso wichtig ist, **womit** er es tut. Drei
Regeln, in dieser Rangfolge:

**1. Urteilskraft läuft auf dem teuren Modell.** Planen, Gegenlesen, Review, jede
Schleifen-Runde, die Mängel finden soll: hier entscheidet sich, ob das Richtige gebaut
wird. Ein hier gesparter Betrag kostet später ein Vielfaches, weil ein Denkfehler im
Plan von jedem Arbeiter pflichtbewusst mitgebaut und danach mühsam wieder ausgebaut
wird. **Am Denken wird nicht gespart.**

**2. Das günstige Modell nur bei exakt bekanntem Output.** Ein Task darf nach unten,
wenn er so scharf spezifiziert ist, dass beide Modelle nachweislich dasselbe Ergebnis
liefern würden: **der Output steht vorher fest, es gibt null Design-Entscheidungen und
null Interpretationsspielraum.** Typisch: ein diktierter Edit an bekannter Stelle, ein
mechanischer Umbenenn-Lauf über viele Dateien, Gerüstcode nach exakter Vorlage. Im
geringsten Zweifel bleibt der Task oben — die Frage lautet nicht „geht das billiger?",
sondern „ist der Output vorher exakt bekannt?".

**3. Nach oben wird nie automatisch eskaliert.** Das jeweils teuerste verfügbare Modell
wählt der Orchestrator nie von sich aus; das ist eine Ansage des Users, kein
Ermessensspielraum. Läuft ein Task heiss, wird er **kleiner geschnitten**, nicht teurer
besetzt.

Praktisch heisst das: Plan-Phase durchgehend teuer, Bau-Phase gemischt (Vertrags- und
Logik-Tasks teuer, mechanische Tasks günstig), Schleifen-Review teuer. Das Modell steht
als Angabe **(f)** im Arbeiter-Auftrag (`<AGENTENORDNER>/vorgehen/03-build.md`) — es
wird pro Task benannt, nicht einmal global gesetzt.
