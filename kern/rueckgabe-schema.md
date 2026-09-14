# Rückgabe-Schema — wie ein Arbeiter meldet

Jeder Arbeiter beendet seinen Auftrag mit genau diesen vier Feldern. Nichts davor,
nichts danach.

```
ERLEDIGT — was fertig ist (Dateien, grüne Tests), je eine Zeile
OFFEN — was aussteht oder als Frage geparkt ist, priorisiert
FINDINGS — Befunde mit Beleg Pfad:Zeile; bei Bau-Tasks der Rot-Beleg
NÄCHSTER SCHRITT — wo ein Nachfolger exakt weitermacht, ein Satz
```

**Warum so streng:** Ein Arbeiter liest unterwegs Dateien, lässt Tests laufen, verwirft
Sackgassen, all das bleibt in seinem eigenen Kontext und wird mit ihm weggeworfen. Die
finale Antwort ist das Einzige, was ihn überlebt. Was dort nicht steht, ist verloren.

**Regeln:**

- Alle vier Felder stehen immer da. Nichts zu melden heisst „—", nicht Feld weglassen.
- Nie nur „fertig" / „erledigt" / „steht oben": es gibt kein Oben.
- Keine rohen Datei-Inhalte, keine ungefilterte Testausgabe. Einzige Ausnahme: der
  Rot-Beleg, also die paar Zeilen des einmal fehlgeschlagenen Testlaufs.
- Offene Entscheidungen gehören unter OFFEN. Ein Arbeiter fragt nie selbst nach; er
  arbeitet den Rest fertig und meldet die Frage.
- Der Orchestrator prüft jede Rückgabe gegen dieses Schema, bevor er einen Task abhakt.
  Fehlt ein Feld, oder fehlt bei einem Logik-Task der Rot-Beleg, gilt der Task als
  nicht erledigt und geht zur Nachbesserung.
- Die `Pfad:Zeile`-Belege sind **Arbeits-Material und bleiben intern**. Sie gehören in
  die Rückgabe, in die Mitschreib-Datei und in den nächsten Auftrag — vor den User
  kommen sie übersetzt, nicht roh (`<AGENTENORDNER>/vorgehen/antwortform.md`).

**Dieselben vier Felder sind auch der Stand-Brief beim Übergeben.** Muss ein Arbeiter
schliessen, weil sein Kontext an der Budget-Grenze steht
(`<AGENTENORDNER>/vorgehen/04-kontext.md`), schliesst er die laufende Arbeitseinheit
sauber ab und gibt genau diese vier Felder zurück. Sie sind dann kein Abschlussbericht,
sondern der Eingang des **frischen** Arbeiters, der die Restarbeit übernimmt: NÄCHSTER
SCHRITT ist sein erster Schritt. Eine Fortsetzung des alten Kontexts gibt es nicht — was
im Brief fehlt, ist verloren, genau wie am Ende eines normalen Auftrags.

Diesen Satz trägt jeder Arbeiter-Auftrag wörtlich: „Deine finale Antwort ist das
Einzige, was ankommt: antworte nie nur mit ‚fertig'."
