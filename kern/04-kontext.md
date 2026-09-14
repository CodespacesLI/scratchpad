# Schritt 4 — Kontext: die knappe Ressource haushalten

Diese Datei gehört zu keiner der drei Phasen allein. Sie läuft quer durch alle drei mit,
denn sie beschreibt die Ressource, an der jede lange Sitzung scheitert: den Kontext.

**Eingang:** eine Sitzung, die länger läuft als ein paar Züge.
**Ausgang:** ein Kontext, der schlank bleibt — oder ein sauberer Übergabepunkt, an dem
ein frischer Kontext die Arbeit ohne Wissensverlust übernimmt.

---

## Warum ein voller Kontext teuer UND schlechter wird

Der Kontext ist alles, was das Modell bei jedem einzelnen Zug erneut liest: die Regeln,
das bisherige Gespräch, jede gelesene Datei, jede Bau-Ausgabe, jede Sackgasse. Er wächst
nur, er schrumpft nie von selbst.

**Teuer**, weil jeder Zug den ganzen bisherigen Kontext erneut liest. Kosten sind nicht
die Summe der Züge, sondern Fenstergrösse **mal** Anzahl der Züge. Ein Lauf, der bei
30k anfängt und bei 200k endet, kostet ein Vielfaches eines Laufs, der durchgehend bei
30k bleibt — bei identischem Ergebnis.

**Schlechter**, weil das Wesentliche im Ballast untergeht. In einem vollen Kontext
stehen die drei wichtigen Zeilen zwischen zwanzigtausend unwichtigen: der Datei-Dump,
den niemand mehr braucht, das Testprotokoll von vor einer Stunde, der verworfene
Lösungsversuch. Das Modell gewichtet dann nicht mehr zuverlässig, was zählt, und der
verworfene Versuch von vorhin kommt als „Idee" zurück.

**Merksatz: Ein voller Kontext ist nicht nur teurer, er ist auch dümmer.**

Die drei Gegenmittel, in dieser Reihenfolge:

1. **Trennen** — der Orchestrator denkt, die Arbeiter lesen und bauen. Der ganze
   Lese-Ballast bleibt im Kontext des Arbeiters und wird mit ihm weggeworfen
   (`<AGENTENORDNER>/vorgehen/03-build.md`).
2. **Verdichten** — jeder Arbeiter meldet nur das Rückgabe-Schema zurück, nie rohe
   Datei-Inhalte, nie ungefilterte Testausgaben
   (`<AGENTENORDNER>/vorgehen/rueckgabe-schema.md`).
3. **Übergeben** — wenn der Hauptkontext trotzdem gross wird, wird er an einem sauberen
   Punkt geschlossen und ein frischer nimmt die Arbeit auf. Das ist der Rest dieser
   Datei.

## Die Mitschreib-Datei — Haltbarkeit für den einzelnen Arbeiter

Ein Arbeiter mit langem Auftrag schreibt seinen Stand fortlaufend mit, statt ihn nur im
eigenen Kontext zu halten. Die Mechanik steht in `03-build.md`, Ausbaustufe 2, und wird
hier nicht wiederholt. Wichtig ist die Abgrenzung:

| Datei | Wem gehört sie | Wozu |
|---|---|---|
| `<AGENTENORDNER>/state/<slug>-mitschrieb.md` | **einem** Arbeiter | überlebt seinen Absturz, ein Nachfolger macht beim ersten offenen Punkt weiter |
| `<AGENTENORDNER>/state/handoff-brief.md` | dem **Orchestrator** | überlebt das Leeren des Hauptgesprächs |
| `<AGENTENORDNER>/state/loop-stand.md` | einer **Schleife** | überlebt die Runden, damit jede Runde frisch starten kann |
| `<AGENTENORDNER>/tasks/<slug>.md` | dem **Feature** | der freigegebene Plan, überlebt alles davon |

Alles unter `<AGENTENORDNER>/state/` ist flüchtiges Arbeitsmaterial: es ist gitignored
und gehört nicht in einen Commit. Der Plan unter `<AGENTENORDNER>/tasks/` gehört
hinein — er wird committet, und wenn er fertig ist, nach
`<AGENTENORDNER>/tasks/done/` verschoben statt gelöscht.

## Das Budget eines Arbeiters — etwa 120 000 Tokens

Der Haushalt gilt nicht nur für das Hauptgespräch. Auch ein Arbeiter läuft voll, und die
Rechnung ist dieselbe: **kein Arbeiter bekommt über etwa 120 000 Tokens hinaus
Folgearbeit.** Ein aufgeblähter Arbeiter-Kontext ist teuer und gleichzeitig schlechter;
ein frischer Arbeiter mit destilliertem Auftrag ist billiger und schärfer.

**Der eigentliche Hebel ist der Schnitt, nicht die Überwachung.** Aufgaben werden so
klein zugeschnitten, dass die Schwelle gar nicht erreicht wird — das Budget ist das
Sicherheitsnetz für den Ausreisser, kein Dauermonitoring.

**Gemessen wird ohne Polling.** Der Orchestrator liest die Zahl nur dort, wo er ohnehin
hinschaut: bei der Fertig-Meldung eines Arbeiters, und einmalig, **bevor** er einem noch
laufenden Arbeiter Folgearbeit gibt. Nicht in Arbeiter-Protokolle hineinlesen, keine
Timer, keine Zwischenstands-Abfragen „nur mal schauen" — jede davon kostet selbst
Kontext und bringt keine Entscheidung.

**Geschlossen wird am nächsten natürlichen Übergabepunkt**, genau wie beim Handoff des
Hauptgesprächs: fertige Datei, abgeschlossene Arbeitseinheit, grüne Test-Runde. Nie
mitten in einer halb geänderten Datei. Der Arbeiter bekommt dafür **genau eine** kurze
Nachricht: „Arbeitseinheit sauber abschliessen, kompakten Stand-Brief zurückgeben."

**Die Restarbeit geht an einen frischen Arbeiter**, mit diesem Stand-Brief und der
Mitschreib-Datei als Eingang — nie als Fortsetzung des alten Kontexts. Sonst erbt der
Nachfolger genau den Ballast, dessentwegen übergeben wurde.

**Eine Ausnahme:** läuft der Arbeiter nur noch Tests oder einen Build zu Ende, ohne neue
Bau- oder Denkarbeit, darf er auslaufen, auch über 120 000. Der Zwang gilt der
Folgearbeit, nicht dem blossen Verifizieren.

## Der Handoff-Zyklus: `/handoff` → `/clear` → `/resume`

Drei Schritte, und nur der erste und der letzte gehören dem Modell.

**1. `/handoff`** — an einem **sauberen Übergabepunkt**: abgeschlossene Phase, fertige
Aufgabe, grüne Test-Runde, gemachter Commit. Nie mitten in einer halb geänderten Datei
und nie mitten in einem offenen Umbau — sonst verliert der Nachfolger genau das Wissen,
das der Brief retten soll. Der Orchestrator destilliert seinen Stand auf etwa eine Seite
und schreibt ihn nach `<AGENTENORDNER>/state/handoff-brief.md`: was erledigt ist, was
offen ist, wo er genau steht, und die Belege, die der Nachfolger braucht. Keine Diffs,
keine Datei-Inhalte, keine Nacherzählung des Gesprächs.

**2. `/clear`** — der User leert das Gespräch. **Das macht der Mensch**, kein Command und
kein Wächter kann es auslösen (siehe „Die Grenze" unten).

**3. `/resume`** — im frischen Gespräch: Brief lesen, **jeden Kernpunkt gegen den
Arbeitsbaum prüfen**, dann beim ersten offenen Punkt weitermachen.

Das Prüfen ist keine Formalie. **Der Brief ist ein Bericht, kein Beweis.** Zwischen dem
Schreiben und dem Lesen kann der User selbst committet, den Branch gewechselt oder
etwas verworfen haben. Deshalb gilt: bei Widerspruch gewinnt immer der Arbeitsbaum, und
die Abweichung wird dem User in einem Satz genannt, statt sie stillschweigend zu
überschreiben.

## Nicht bis zur Grenze warten — und die Übergabe bleibt Handarbeit

Der Zyklus rettet die Sitzung, aber **wann** er läuft, entscheidet über die Güte des
Briefs. Faustregel: übergeben ab etwa **120 000 Tokens** (~60 Prozent des Fensters) —
nicht erst, wenn der Budget-Sensor sich meldet.

Der Grund ist unbequem: den Brief schreibt genau der Kontext, der schon voll ist. **Eine
Zusammenfassung aus einem degradierten Kontext erbt dessen Lücken.** Was das späte Fenster
übersieht, fehlt auch im Brief — und der Nachfolger startet mit einem sauber formatierten
Irrtum, den er für den Stand hält. Die Schwelle des Sensors ist das Sicherheitsnetz, nicht
der Arbeitsmodus.

**Ausgelöst wird die Übergabe vom Menschen, nicht von der Sitzung.** Erreicht die Sitzung
die Faustregel, **meldet** sie das in einem Satz: der Kontext ist bei etwa 120k, jetzt
wäre `/handoff` fällig. Danach tippt der Teilnehmer selbst: `/handoff`, dann `/clear`,
dann `/resume`. Drei Tastenfolgen, bewusst nicht wegautomatisiert.

Das ist eine Entscheidung, keine fehlende Funktion. Die Übergabe ist der Punkt, an dem
Arbeitsstand verloren gehen kann: wer sie selbst auslöst, sieht den Brief, bevor der
Nachfolger auf ihm aufsetzt, und merkt, wenn etwas Wesentliches fehlt. Eine Sitzung, die
sich selbst ablöst, nimmt dem Menschen genau diesen Blick — und bei zwei Sitzungen auf
demselben Arbeitsbaum überschreiben sie sich gegenseitig. Der Kontext-Wächter darf
warnen und den Zug beenden; **starten darf er nichts.**

## Der Budget-Sensor: `guard_context_budget`

Ein Wächter am Zug-Ende misst den echten Kontextstand aus dem Sitzungsprotokoll — keine
Schätzung, keine Heuristik, eine Zahl.

**Default: eine einzige Warnung.** Ab **150 000** Tokens meldet er sich **einmal pro
Sitzung**: „Kontext bei ~Xk — jetzt `/handoff`, dann `/clear` + `/resume`." Er blockt
nichts und wiederholt sich nicht. Der User entscheidet, ob er den Zyklus jetzt fährt
oder die Diskussion zu Ende führt. **Warum nicht automatisch:** ein erzwungener Handoff
mitten in einem Gespräch ist Bevormundung; die Warnung liefert dieselbe Information ohne
Kontrollverlust.

**Zwei Schalter, beide als Umgebungsvariable — eine Zeile im Terminal, sofort wirksam,
nichts zu editieren:**

| Schalter | Wirkung |
|---|---|
| `SCRATCHPAD_AUTO_HANDOFF=1` | Statt zu warnen, beendet der Wächter den Zug mit der Auflage, den Brief **jetzt** zu schreiben. Opt-in-Stufe für lange unbeaufsichtigte Läufe. |
| `SCRATCHPAD_KONTEXT_BUDGET=<zahl>` | Senkt (oder hebt) die Schwelle. Default 150000; ein unbrauchbarer Wert fällt auf den Default zurück. |

Zum Vorführen wird die Schwelle auf einen Wert gesenkt, den die laufende Sitzung längst
überschritten hat — dann feuert der Sensor im nächsten Zug:

```
SCRATCHPAD_KONTEXT_BUDGET=20000 claude          # Warnung provozieren (Mac/Linux)
SCRATCHPAD_KONTEXT_BUDGET=20000 SCRATCHPAD_AUTO_HANDOFF=1 claude   # erzwungener Brief

# Windows (PowerShell):
$env:SCRATCHPAD_KONTEXT_BUDGET='20000'; claude
$env:SCRATCHPAD_KONTEXT_BUDGET='20000'; $env:SCRATCHPAD_AUTO_HANDOFF='1'; claude
```

## Die Grenze — ehrlich dazugesagt

**`/handoff`, `/clear` und `/resume` bleiben Handarbeit.** Ein Hook kann das Gespräch
nicht leeren, keinen neuen Command starten und keine Nachfolge-Sitzung öffnen; er kann
nur den laufenden Zug beenden und eine Auflage mitgeben. Auch mit
`SCRATCHPAD_AUTO_HANDOFF=1` ist deshalb nur die **Auflage** automatisch, den Brief jetzt
zu schreiben — getippt werden die drei Schritte vom Menschen. Das ist teils eine Grenze
des Werkzeugs und teils Absicht, und beides wird in der Vorführung genannt statt
verschwiegen.

**Hinter der Grenze weiter:** wer stundenweise weggeht und den Zyklus trotzdem laufen
lassen will, fährt ihn von **außerhalb** der Sitzung — `python treiber.py auto
"<auftrag>"` startet headless Sitzungen nacheinander, erkennt Brief und Sitzungs-Ende
und reicht den Brief an die nächste frische Sitzung weiter. Der Preis (Freigaben
abgeschaltet) und die Not-Aus-Wege stehen im `README.md`, die Entscheidungen dahinter
in `KONZEPT.md`, Kern-Entscheidungen 4 und 5.

Genauso ehrlich: der Sensor misst nur die **Grösse**, nicht die **Güte** des Kontexts.
Ob die 140k voller nützlicher Entscheidungen oder voller verworfener Sackgassen sind,
kann er nicht wissen. Deshalb warnt er und urteilt nicht.

**Merksatz: Das Harness misst, das Modell urteilt, der User entscheidet.**

Genau in dieser Reihenfolge — und genau deshalb ist der Kontextstand der einzige Punkt,
an dem in diesem Harness ein Wächter von sich aus aktiv wird: er ist der einzige, der
sich deterministisch messen lässt. Alles andere (Schleife oder Arbeiter? Handoff jetzt
oder nach der Diskussion?) ist eine Urteilsfrage und steht als Regel in Prosa, nicht als
Heuristik in einem Hook. Ein ratender Wächter produziert Fehlalarme, der User klickt sie
weg — und übersieht danach auch die echten Treffer.
