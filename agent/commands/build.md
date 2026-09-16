---
description: Baut einen freigegebenen Plan Task fuer Task ab, mit parallelen Arbeitern
argument-hint: <Pfad zum freigegebenen Plan>
risk: destructive
cost: expensive
---

Lies `<AGENTENORDNER>/vorgehen/03-build.md` und folge ihr Schritt fuer Schritt.

Eingabe: $ARGUMENTS — der Plan liegt unter `<AGENTENORDNER>/tasks/<slug>.md`; ist er
fertig, wandert er nach `<AGENTENORDNER>/tasks/done/` und wird nie geloescht.

**Du baust alle offenen Tasks des Plans am Stueck.** Wellen sind eine Reihenfolge, keine
Haltepunkte: nach jeder verifizierten Welle startest du sofort die naechste, ohne
Zwischenbericht und ohne auf eine Freigabe zu warten. Steht der Plan schon auf
`Status: im-bau`, ist das eine Wiederaufnahme, und du machst beim ersten offenen Task
weiter. Anhalten darfst du nur aus zwei Gruenden: (a) eine echte Blockade, die der Plan
nicht regelt und ohne Entscheidung des Users falsch gebaut wuerde, oder (b) der Kontext
ist voll: der Kontext-Waechter meldet sich bei etwa 120k Tokens (deinen eigenen
Fuellstand siehst du nicht, der Waechter misst ihn). Dann laufende
Arbeiter fertig werden lassen, abhaken, keine neue Welle starten und dem User sagen:
`/handoff`, `/clear`, `/resume`, danach wieder `/build`. Nennt der User in $ARGUMENTS
ausdruecklich eine Teilmenge, gilt diese; von dir aus teilst du den Plan nie in Runden auf.

Traegt ein Task das Feld `Vorlage:`, steht im Auftrag des Arbeiters: zuerst die Vorlage
ins Projekt kopieren und auf den Task zuschneiden, die Herkunftszeile als erste
Kommentarzeile setzen, nichts neu schreiben und nichts nachholen
(`<AGENTENORDNER>/vorgehen/referenzen-holen.md`, Abschnitt „Regeln fuer das Kopieren").

Modus A gilt: du bist der Orchestrator und baust nicht selbst. Jeden Task gibst du ueber
das Task-Werkzeug an einen Arbeiter; die Rolle steht im Task (`backend`, `frontend`,
`fullstack`) und das passende Playbook aus `<AGENTENORDNER>/vorgehen/rollen.md` schreibst
du in den Auftrag hinein. Mehrere Arbeiter einer Welle startest du in einer Nachricht,
damit sie gleichzeitig laufen.

**Immer im Hintergrund starten, nie synchron.** Ein synchron gestarteter Arbeiter haengt
an deinem laufenden Zug: solange er baut, bist du nicht ansprechbar, und ein Abbruch im
Gespraech reisst seine Arbeit mit ab. Im Hintergrund laeuft er weiter, das Gespraech
bleibt frei, und die Fertigstellung kommt als Meldung zurueck.

**Ein Arbeiter mit mehreren Aufgaben delegiert weiter**, statt alles im eigenen Fenster
zu erledigen — Aufgaben in einem Fenster addieren sich nicht, sie multiplizieren sich,
weil jeder Zug den gesamten bisherigen Kontext erneut liest. Selbst erledigen darf er
nur, was zusammen unter ~15 Minuten und unter fuenf Dateien bleibt. Diese Ansage
schreibst du in den Auftrag hinein, zusammen mit dem Budget: ueber ~120k Tokens hinaus
bekommt kein Arbeiter Folgearbeit, er schliesst ab, gibt einen kompakten Stand-Brief
zurueck, und der Rest geht an einen frischen Arbeiter.

**Jede Welle ist ein frischer Dispatch.** Keine Welle setzt die Arbeiter der Vorwelle
fort; nachgebessert wird ueber **einen** eigens gestarteten Fix-Arbeiter, nie ueber
mehrere parallele Fixer auf demselben Code — zwei Fixer in derselben Datei
ueberschreiben sich gegenseitig.

Modell pro Task benennen: Default ist das teure Modell. Auf das guenstige geht ein Task
nur, wenn sein Output vorher exakt bekannt ist und null Design-Entscheidungen offen sind.
Nach oben wird nie automatisch eskaliert.

Kannst du keine Arbeiter starten, gilt stattdessen Modus B aus derselben Anleitung:
du arbeitest die Tasks selbst und nacheinander ab. Sag dem User dann zu Beginn in
einem Satz, dass ohne parallele Arbeiter der sequenzielle Weg laeuft.

Fragen der Arbeiter sammelst du und legst sie dem User am Ende gebuendelt vor.
