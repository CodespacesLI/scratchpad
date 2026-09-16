---
description: Schliesst den Hauptkontext an einem sauberen Uebergabepunkt ab und schreibt den Stand nach state/handoff-brief.md
argument-hint: <optionaler Fokus, z.B. "nur der Import-Ablauf"; leer = der ganze Auftrag>
risk: repeatable
cost: cheap
---

Schreibt den Stand des Hauptgesprächs destilliert nach
`<AGENTENORDNER>/state/handoff-brief.md`, damit der User danach `/clear` machen und mit
`/resume` in einem frischen, schlanken Kontext weiterarbeiten kann — ohne Wissensverlust.
Hintergrund: `<AGENTENORDNER>/vorgehen/04-kontext.md`.

`$ARGUMENTS` ist ein optionaler Fokus-Hinweis; leer heisst der komplette laufende Auftrag.

## Wann

An einem **sauberen Übergabepunkt**: abgeschlossene Phase, fertige Aufgabe, grüne
Test-Runde, gemachter Commit. **Nie mitten in einer halb geänderten Datei und nie in
einem offenen Umbau.** Steht gerade etwas halb offen: erst zu Ende bringen, dann diesen
Command.

## Schritt 1 — Stand einsammeln, billig

Nur diese Quellen, jeweils verdichtet, **keine Diffs und keine Datei-Inhalte**:

- `git status --short` und `git log --oneline -5` — Branch, letzter Commit, Umfang.
- Der Plan unter `<AGENTENORDNER>/tasks/<slug>.md`, falls einer läuft: Abhak-Stand zählen und die
  **offenen** Task-Titel ziehen (nur Titel).
- Vorhandene Mitschreib-Dateien unter `<AGENTENORDNER>/state/` nur **nennen**, nicht
  einlesen — sie stehen ohnehin schon auf der Platte.
- Was aus dem laufenden Gespräch kommt: erledigte Schritte, Rot-Belege, getroffene
  Entscheidungen, Stolpersteine. Aus dem Kopf, nicht neu erarbeiten.

Kein Erkundungslauf, kein Testlauf, keine Arbeiter. Das hier ist ein Schreib-Schritt,
keine Untersuchung.

## Schritt 2 — Destillieren, das ist die eigentliche Arbeit

Der Brief ist **maximal etwa eine Seite** und hat genau vier Abschnitte:

- **ERLEDIGT** — was fertig ist, je eine Zeile, mit Beleg (Datei, Commit, Testname).
- **OFFEN** — was aussteht, priorisiert, je eine Zeile.
- **WO ICH STEHE** — Branch, letzter Commit, was gerade in Arbeit war, zwei bis drei
  Sätze. Der Satz, den der Nachfolger zuerst liest.
- **BELEGE UND STOLPERSTEINE** — `Pfad:Zeile` plus Kernaussage, Testbezeichner, bekannte
  Fallstricke („die Migration muss vor dem Testlauf laufen").

Nicht in den Brief: rohe Unterschiede, kopierte Code-Blöcke, Testprotokolle, die
Nacherzählung des Gesprächs, Begründungen in Absätzen. Ein Entscheid ist ein Halbsatz.

## Schritt 3 — Übergeben

Brief schreiben (bestehende Datei wird überschrieben), danach dem User in **einer** Zeile
sagen, was er jetzt tut:

> Stand steht in `<AGENTENORDNER>/state/handoff-brief.md` — mach `/clear` und dann
> `/resume`.

Danach **nichts mehr selbst bauen**. Der Brief liegt, den Rest macht der Mensch: er tippt
`/clear` und danach `/resume`. **Kein Command und kein Wächter kann das auslösen** — ein
Hook kann den Zug beenden und eine Auflage mitgeben, aber er kann das Gespräch nicht
leeren und keinen Befehl starten. Wer hier weiterarbeitet, schreibt in genau den vollen
Kontext zurück, den der Brief gerade abgelöst hat.
