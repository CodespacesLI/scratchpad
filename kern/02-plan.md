# Schritt 2 — Plan: vom Brief zu atomaren Tasks

**Eingang:** der bestätigte Brief aus Schritt 1 oder eine bereits klare Absicht. Ist die
Absicht unklar, geh zuerst zurück zu `<AGENTENORDNER>/vorgehen/01-brainstorm.md`.

**Ausgang:** eine Plan-Datei `<AGENTENORDNER>/tasks/<slug>.md` mit `Status: entwurf`, die der User
freigibt. Dieser Schritt schreibt Plan-Prosa, keinen Produktivcode.

## Phase 1 — Kontext laden

1. Projekt-Konventionen lesen: die Regel-Datei des Projekts im Wurzelverzeichnis
   (`CLAUDE.md` oder `AGENTS.md`), dazu Regeln des betroffenen Bereichs.
2. Den Code durchsuchen, statt zu raten: Welche Bausteine gibt es schon (Ansichten,
   Dienste, Datenzugriffe)? Welches ähnliche Feature ist die Referenz? **Wiederverwenden
   schlägt neu bauen.**

> Modus A: Diese Suche gehört in einen Lese-Arbeiter, der nur die Fundstellen
> (Pfad + ein Satz, wofür) zurückgibt, nicht die Datei-Inhalte. Modus B: selbst suchen,
> aber gezielt: nur die Treffer notieren, nicht ganze Dateien lesen.

## Phase 2 — Entwurf (intern, noch nicht ausgeben)

- **Ablauf aus Nutzersicht:** wer, in welcher Reihenfolge, was sieht er?
- **Betroffene Schichten:** Daten → Logik → Schnittstelle → UI.
- **Wiederverwendung:** welche bestehenden Bausteine werden genutzt oder erweitert?
- **Neu:** was wird neu gebaut, und warum passt nichts Bestehendes?
- **Randfälle, Zugriffsrechte, sichtbare Texte.**
- **Offene Entscheidungen**, je mit deiner Empfehlung.

## Phase 3 — Gegenleser (Pflicht)

Der Entwurf geht an einen skeptischen Zweitleser. **Modus A:** ein eigener Arbeiter, der
den Entwurf bekommt und nichts sonst. **Modus B:** ein harter Rollenwechsel im selben
Chat: du liest deinen eigenen Entwurf als Gegner, nicht als Autor.

Zwei Vorgaben, beide nicht verhandelbar:

- **Der Gegenleser bekommt NUR den Entwurf** — nicht den Gesprächsverlauf, nicht die
  Fundstellen aus Phase 1, nicht die Begründungen des Autors. Wer die Begründung schon
  kennt, liest wohlwollend mit statt adversarial: er prüft, ob der Entwurf zur
  Begründung passt, statt ob die Begründung trägt. Der frische Kontext ist der
  eigentliche Wirkstoff dieser Phase, nicht die Prüfliste.
- **Entwurf UND Gegenleser laufen auf dem teuren Modell.** Hier zählt Urteilskraft, und
  ein hier gesparter Betrag kostet in der Bau-Phase ein Vielfaches: ein Denkfehler im
  Plan wird von jedem Arbeiter pflichtbewusst mitgebaut. Sparen gehört in die
  mechanische Umsetzung, nicht in die Planung
  (`<AGENTENORDNER>/vorgehen/rollen.md`).

Der Auftrag an den Gegenleser, sechs Prüfpunkte:

1. **Zu viel gebaut**: geht es einfacher, und reicht das einfachere?
2. **Zu wenig gebaut**: fehlen Randfälle, Rechte, Fehler- oder Leerzustände?
3. **Wiederverwendung verpasst**: gibt es das im Projekt schon?
4. **Schichten-Verstoss**: Logik in der Oberfläche, Rechteprüfung an der falschen
   Stelle?
5. **Lücken im Ablauf**: Abbruch, Fehler, leere Daten, fehlende Rechte.
6. **Reihenfolge**: ist jeder Schritt für sich testbar, oder wird erst am Ende sichtbar,
   ob etwas funktioniert?

Antwort: nummerierte Einwände, je mit Begründung und Schweregrad (Blocker / Wichtig /
Nebensache), oder explizit das Wort **KONSENS**, wenn nichts Substanzielles offen ist.

## Phase 4 — Konsens-Runde

Jeden Einwand entweder einarbeiten oder begründet ablehnen, dann den überarbeiteten
Entwurf ein zweites Mal gegenlesen lassen. **Maximal 2 Runden.** Danach wird der Plan so
präsentiert, wie er ist; die Streitpunkte kommen mit beiden Positionen als offene Punkte
in Zone 2, und der User entscheidet. Den Gegenleser-Dialog nicht ausgeben: nur die
daraus getroffenen Entscheidungen.

## Phase 5 — Ausgabe in drei Zonen

**Zone 1: Kurzfassung, maximal 5 Zeilen, Alltagssprache.** Was wird gebaut, wie fühlt
es sich für den User an. Keine Dateinamen, keine Klassen.

**Zone 2: Ablauf und Entscheidungen.** Der Nutzer-Ablauf als nummerierte Schritte;
getroffene Entscheidungen je eine Zeile; offene Punkte für den User.

**Zone 3: atomare Tasks** im Format aus `<AGENTENORDNER>/vorgehen/task-format.md`. Jeder
Task ist so geschnitten, dass ein Arbeiter ihn unbeaufsichtigt abarbeiten kann: eigene
Files-Liste, eigene Akzeptanzkriterien, eigener Test. Tasks ohne offene Abhängigkeit
dürfen später parallel laufen. Deshalb müssen ihre Files-Listen disjunkt sein
(`<AGENTENORDNER>/vorgehen/rollen.md`).

## Plan-Datei ablegen

Der fertige Plan wird als `<AGENTENORDNER>/tasks/<slug>.md` gespeichert. Der Kopf trägt
die „Fertig heisst was"-Liste und die Status-Zeile, beim Anlegen exakt
`Status: entwurf`. Der Plan wird committet, er ist kein flüchtiges Arbeitsmaterial.

**Abschluss:** Der User gibt den Plan frei. Erst dann setzt Schritt 3 die Kopfzeile auf
`Status: im-bau` und beginnt zu bauen.
