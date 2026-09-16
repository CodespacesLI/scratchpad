# Schritt 3 — Build: den Plan abarbeiten

**Eingang:** ein vom User freigegebener Plan unter `<AGENTENORDNER>/tasks/<slug>.md` mit
offenen Tasks.
Kein Plan gefunden → auf Schritt 2 (`<AGENTENORDNER>/vorgehen/02-plan.md`) verweisen und
stoppen. Dieser Schritt plant nicht. Er baut nur, was der Plan festschreibt.

**Ausgang:** alle Tasks abgehakt oder begründet gestrichen, `Status: fertig`, Plan nach
`<AGENTENORDNER>/tasks/done/` verschoben, Statusbericht plus ein gebündeltes Frage-Gate.

**Beim Start** die Kopfzeile des Plans von `Status: entwurf` auf `Status: im-bau` setzen,
exakt diese Zeichenkette. Ein Wächter liest sie. Steht sie schon auf `Status: im-bau`, ist
das eine Wiederaufnahme (etwa nach `/handoff` → `/clear` → `/resume`): die Zeile bleibt,
und gebaut wird ab dem ersten offenen `- [ ]`-Task. Abgehakte Tasks werden nicht noch
einmal angefasst.

## Am Stück bis zum Ende

Ein Build-Auftrag heisst: **alle offenen Tasks des Plans, am Stück.** Wellen sind eine
Reihenfolge für die Arbeiter, keine Haltepunkte. Nach einer Welle startet sofort die
nächste; es gibt keine „Runde 1", nach der auf eine Freigabe gewartet wird, und keine
Teilmenge, die für „die nächste Runde" liegen bleibt. Der Plan ist schon freigegeben,
ein Zwischen-Okay braucht es nicht.

Angehalten wird **nur** aus einem dieser zwei Gründe:

1. **Echte Blockade.** Eine Frage, die der Plan nicht regelt und ohne deren Antwort der
   Task falsch gebaut würde. Alles andere wird geparkt und am Schluss-Gate gestellt
   (Regel 3), und die übrigen Tasks laufen weiter. Auch bei einer Blockade wird nur
   angehalten, was von ihr abhängt, sofern sich der Rest sauber davon trennen lässt.
2. **Kontext voll.** Der Orchestrator sieht seinen eigenen Füllstand nicht. Der Auslöser
   kommt deshalb von aussen: in Claude Code meldet sich der Kontext-Wächter bei etwa
   120 000 Tokens, in Codex (ohne Wächter) sagt der User, dass `/status` etwa 120 000
   Tokens zeigt. Dann: die laufenden Arbeiter fertig werden lassen, ihre
   Tasks prüfen und abhaken, keine neue Welle mehr starten, und dem User in einem Satz
   sagen, dass jetzt `/handoff`, `/clear`, `/resume` und danach wieder `/build` dran sind
   (in Codex: eine Nachricht, die den Stand nach
   `<AGENTENORDNER>/state/handoff-brief.md` schreibt, dann `/new`, dann eine Nachricht,
   die den Brief liest und prüft, danach wieder `Baue:`). Der Nachfolger macht beim
   ersten offenen Task weiter (`<AGENTENORDNER>/vorgehen/04-kontext.md`).

Nennt der User in seinem Auftrag **ausdrücklich** eine Teilmenge („nur Task 1 bis 3"),
gilt diese Teilmenge. Von sich aus teilt der Orchestrator den Plan nie auf.

---

## Modus A (Default): ein Kopf, viele Hände

Ein einziger Chat, der gleichzeitig liest, baut und testet, läuft voll: mit
Datei-Inhalten, Bau-Ausgaben, Sackgassen. Ein voller Kontext wird teuer, und die
Antworten werden schlechter. Deshalb wird getrennt: **der Orchestrator denkt, die
Arbeiter bauen.**

### Die neun Regeln

1. **Der Orchestrator baut nie selbst.** Er liest den Plan, schneidet Wellen, startet
   Arbeiter, prüft Rückgaben und hakt ab. Einzige Ausnahme: ein trivialer
   Ein-Zeilen-Edit, bei dem das Starten eines Arbeiters teurer wäre als die Arbeit.
2. **Arbeiter arbeiten isoliert und melden verdichtet.** Ein Arbeiter bekommt genau einen
   Task und gibt am Ende nur das Rückgabe-Schema zurück, nie rohe Datei-Inhalte, nie
   ungefilterte Testausgaben.
3. **Arbeiter stellen keine Fragen.** Wer auf eine offene Entscheidung stösst, macht den
   Rest des Tasks fertig und meldet die Frage unter OFFEN. Der Orchestrator sammelt alle
   Fragen und legt sie dem User an **einem** Gate am Ende vor, nicht tröpfchenweise.
4. **Der Orchestrator prüft, statt zu glauben.** „Fertig" ist keine Information.
5. **Abhaken sofort, pro Task**, nie gesammelt am Schluss.
6. **Kein `git push`.** Ein Commit pro logischem Schritt ist richtig; das Hochladen macht
   der Mensch.
7. **Arbeiter werden immer im Hintergrund gestartet, nie synchron.** Ein synchron
   gestarteter Arbeiter hängt am laufenden Zug des Hauptgesprächs: solange er baut, ist
   der Orchestrator nicht ansprechbar, und ein Abbruch im Chat — ein versehentliches
   ESC, eine Rückfrage des Users — reisst die Arbeit des Arbeiters mit ab. Im
   Hintergrund läuft er unabhängig weiter, der Chat bleibt frei für den User, und die
   Fertigmeldung kommt zurück, wenn sie fertig ist.
8. **Ein Arbeiter mit mehreren Aufgaben delegiert weiter.** Der Orchestrator-Vertrag
   endet nicht beim Hauptgespräch: bekommt ein Arbeiter mehrere Aufgaben, startet er für
   die weiteren selbst Arbeiter, statt alles in seinem eigenen Fenster zu erledigen.
   Aufgaben in einem Fenster addieren sich nicht, sie **multiplizieren** sich, weil jeder
   Zug den gesamten bisherigen Kontext erneut liest. Die Grenze gilt in beide Richtungen:
   selbst erledigen darf er, was zusammen unter etwa 15 Minuten und unter fünf Dateien
   bleibt oder denselben frisch gelesenen Zustand braucht — ein Dispatch hat Fixkosten,
   und für zwei Zeilen lohnt er sich nicht. Sobald zwei Aufgaben eigenen Scope haben,
   wird delegiert. **Im Zweifel delegieren.**
9. **Jede Runde ist ein frischer Dispatch.** Keine Review- oder Nachschärf-Runde setzt
   die Arbeiter der Vorrunde fort; die Vorrunde hat ihren Ballast im Kontext, der
   Nachfolger bekommt nur den Befund. Und gefixt wird über **einen** nacheinander
   gestarteten Fix-Arbeiter, nie über mehrere parallele Fixer auf demselben Code: zwei
   schreibende Arbeiter im selben Arbeitsbaum kollidieren, und was der eine schreibt,
   überschreibt der andere.

### Vorfrage — Schleife oder Arbeiter?

Bevor irgendetwas gestartet wird: Ist diese Arbeit ein **Dispatch** (Arbeiter pro Task)
oder eine **Schleife** (derselbe Auftrag, wieder und wieder, bis ein Kriterium hält)?

Eine Schleife lohnt sich **nur, wenn alle drei Bedingungen zusammen** erfüllt sind:

1. **Es gibt ein deterministisches, von aussen messbares Fertig-Kriterium** — Tests
   grün, Prüfwerkzeug leer, „N saubere Runden in Folge". Das Kriterium liegt ausserhalb
   des Modells; **die Schleife darf sich nicht selbst für fertig erklären können.**
2. **Jede Runde startet mit frischem Kontext** — der ganze Zustand (Rundenzähler,
   Streak, bisherige Befunde) liegt in einer Datei, nicht im Gesprächsverlauf. Genau
   das macht die Schleife billig: der Kontext wächst über die Runden nicht mit.
3. **Die Konvergenz wird überwacht** — eine Runden-Obergrenze und eine Pendel-Erkennung:
   wird dieselbe Stelle zum zweiten Mal gegensätzlich „repariert", wird abgebrochen und
   der Streitfall dem User vorgelegt, statt endlos hin und her zu pendeln.

Fehlt auch nur eine der drei, wird dispatcht. **Der Plan-Abbau ist der Regelfall für
Dispatch:** jeder Task hat eigenen Scope, eigene Akzeptanzkriterien, und ist danach
FERTIG — es gibt nichts zu wiederholen. Eine Schleife wäre hier reine Wiederholung
ohne Erkenntnisgewinn.

**Merksatz: Dispatch für Erzeugen, Loop für Konvergieren.**

Der typische Schleifen-Fall in diesem Vorgehen ist das Nachschärfen des fertigen
Unterschieds: Review findet Mängel → Fix behebt sie test-first → nächste Runde prüft
das Ergebnis, bis zwei Runden in Folge sauber sind. Dafür gibt es den Command `/loop`.

### Schritt 1 — Wellen bilden

Alle offenen `- [ ]`-Tasks aus Zone 3 lesen. Eine Welle sind Tasks, die (a) keine offene
Abhängigkeit mehr haben und (b) paarweise disjunkte `Files:`-Listen tragen. Schema und
Vertrag bilden die erste Welle allein, die Verdrahtung die letzte Welle allein. Die
Regeln dazu stehen in `<AGENTENORDNER>/vorgehen/rollen.md`.

Die Wellen werden nacheinander abgearbeitet, ohne Pause dazwischen: ist eine Welle
verifiziert und abgehakt (Schritt 3), startet sofort die nächste, ohne auf den User zu
warten und ohne Zwischenbericht (siehe „Am Stück bis zum Ende").

### Schritt 2 — Arbeiter beauftragen

Der Arbeiter wird **im Hintergrund** gestartet (Regel 7), und sein Auftrag trägt diese
neun Angaben. Fehlt eine, läuft der Arbeiter ins Leere oder ins Uferlose:

> **(a) Exakte Dateiliste** aus dem Task: kein „schau dich um", kein „finde die
> passende Stelle".
> **(b) Lese-Ansage:** gezielt Ausschnitte lesen statt ganzer Dateien, grosse Ausgaben
> filtern statt roh zu übernehmen.
> **(c) Hartes Limit: „höchstens 30 Werkzeug-Aufrufe, danach melde, was du hast."**
> Eine Zahl, kein „halte dich kurz" — nur die Zahl ist prüfbar. Diese Zahl ist der
> Kosten-Regler: die Rechnung ist Aufrufe **mal** Fenstergrösse, und jeder Aufruf
> vergrössert zugleich das Fenster für alle folgenden. Ein Auftrag, der mehr als 30
> braucht, ist zu gross geschnitten — dann wird er **aufgeteilt, nicht das Limit
> erhöht.**
> **(d) Test-zuerst-Vertrag:** „Schreibe ZUERST den Test zu den Akzeptanzkriterien, lass
> ihn **rot** laufen, implementiere dann bis **grün**. Der Rot-Beleg gehört in FINDINGS."
> Ohne diesen Satz baut der Arbeiter erst den Code und hängt den Test hinterher an, und
> ein Test, der nie rot war, beweist nichts.
> **(e) Rückgabe-Schema** aus `<AGENTENORDNER>/vorgehen/rueckgabe-schema.md`, samt dem
> Satz „Deine finale Antwort ist das Einzige, was ankommt: antworte nie nur mit
> ‚fertig'."
> **(f) Modell:** Default ist das **teure** Modell. Auf das günstige geht ein Task nur,
> wenn sein **Output vorher exakt bekannt ist und null Design-Entscheidungen** offen
> sind — ein diktierter Edit an bekannter Stelle, ein mechanischer Umbenenn-Lauf,
> Gerüstcode nach exakter Vorlage. Im geringsten Zweifel: teuer. Nach oben wird nie
> automatisch eskaliert. Die Begründung steht in
> `<AGENTENORDNER>/vorgehen/rollen.md`.
> **(g) Pfad der Mitschreib-Datei** bei länger laufenden Aufträgen:
> `<AGENTENORDNER>/state/<slug>-mitschrieb.md`. Der Orchestrator gibt ihn im Auftrag
> mit, sonst schreibt der Arbeiter seinen Stand nirgends mit und ein Abbruch kostet die
> ganze Arbeit (Ausbaustufe 2 weiter unten).
> **(h) Das Budget:** „Kommst du über etwa 120 000 Tokens, schliess die laufende
> Arbeitseinheit sauber ab und gib einen kompakten Stand-Brief zurück." Die Restarbeit
> geht danach an einen frischen Arbeiter, nie als Fortsetzung. Die Begründung und die
> Ausnahme für auslaufende Test- und Build-Läufe stehen in
> `<AGENTENORDNER>/vorgehen/04-kontext.md`.
> **(i) Die Vorlage des Tasks**, wenn er das Feld `Vorlage:` trägt: „Kopiere zuerst die
> Vorlage ins Projekt und schneide sie auf den Task zu; setze die Herkunftszeile
> `Vorlage: <repo>@<commit> <pfad> (<Lizenz>)` als erste Kommentarzeile; schreibe nichts
> neu, wofür die Vorlage bereitliegt, und hole nichts nach." Die Regeln stehen in
> `<AGENTENORDNER>/vorgehen/referenzen-holen.md`, Abschnitt „Regeln fuer das Kopieren".

Bekommt ein Arbeiter ausnahmsweise mehr als eine Aufgabe, trägt sein Auftrag zusätzlich
die Ansage aus Regel 8: jede weitere Aufgabe selbst weiterdelegieren, statt sie im
eigenen Fenster zu erledigen.

Dazu den Datei-Zaun-Satz aus `<AGENTENORDNER>/vorgehen/rollen.md`.

### Schritt 3 — Verifizieren und abhaken, nach jedem Task

1. Rückgabe gegen das Schema prüfen: alle vier Felder da?
2. `git status` und Änderungsumfang plausibel: nur Dateien aus der Files-Liste?
3. Den Test des Tasks selbst gezielt laufen lassen: grün?
4. Bei Logik-Tasks: **Rot-Beleg vorhanden?** Fehlt er, gilt der Task als nicht erledigt,
   wird nicht abgehakt und geht als Nachbesserung an einen frischen Arbeiter.
5. Erst dann `- [ ] offen` → `- [x] erledigt` im Plan, und Commit für diesen Schritt.

### Schritt 4 — Abschluss

Hält der Bau aus einem der zwei Gründe aus „Am Stück bis zum Ende" an, bleibt der Plan auf
`Status: im-bau` und am Platz; der User bekommt nur den Grund und den nächsten Schritt.

Erst wenn alle Tasks abgehakt oder begründet gestrichen sind: `Status: im-bau` → `Status: fertig`,
Plan-Datei nach `<AGENTENORDNER>/tasks/done/` verschieben, nie löschen. Dann der
Statusbericht nach `<AGENTENORDNER>/vorgehen/antwortform.md`; inhaltlich: was gebaut
wurde, was offen blieb, was verworfen wurde und warum — im Flow erzählt, nicht als
Liste abgearbeiteter Tasks. Danach alle geparkten Fragen an **einem** Gate. Die
Antworten des Users vollständig umsetzen, notfalls mit einer weiteren Welle.

**Das Frage-Gate ist eine Übersetzungsstelle, kein Durchreich-Ort.** Die Arbeiter
melden ihre offenen Punkte technisch, mit `Pfad:Zeile`-Belegen — genau so gehören sie
NICHT vor den User. Jede geparkte Frage wird nach der Antwortform präsentiert,
verbindlich:

- **Am Auslöser ansetzen und im Flow erzählen:** wer im Produkt was tut, was das
  System daraufhin macht, an welcher Stelle es kippt, was der Nutzer davon sieht — als
  Kette in Sätzen, nicht als Stationen-Liste. Mehrere Fragen zum selben Thema teilen
  sich EINEN Einstieg und stehen darunter als kompakte Punkte.
- **Maximal 5 Zeilen pro Frage**, und die Optionen stehen direkt dabei, nicht als
  zweites Häppchen nach einer Rückfrage. Ein Gate mit mehreren Fragen wird Thema für
  Thema abgearbeitet, nicht als Liste ausgeschüttet.
- **Optionen als ganze Sätze aus User-Sicht**, nicht als Stichwort-Paare. Ist eine
  davon klar richtig, wird sie genannt und begründet, statt drei gleichwertige
  Varianten auszubreiten.
- **Die `Pfad:Zeile`-Belege der Arbeiter bleiben draussen** — sie kommen nur in die
  Antwort, wenn der User danach fragt oder sie zum Entscheiden braucht, dann direkt und
  ohne Verpackung. Kein Technik-Anhang von selbst.
- **Gekürzt wird nie, was weh tut:** ein roter Test, ein übersprungener Schritt, ein
  Datenverlust-Risiko steht drin, auch wenn die Antwort dadurch länger wird.

Vorher — so kommt es vom Arbeiter, so bleibt es nicht:

> OFFEN: `SpeichernButton.tsx:41` — kein Disabled-State während des Requests,
> Doppel-Submit möglich. Debounce oder Server-Idempotenz?

Nachher — so geht es an den User:

> Ein Nutzer füllt das Formular „Neuer Eintrag" aus und klickt auf Speichern. Bei
> langsamer Verbindung bleibt der Knopf aktiv, ein zweiter Klick schickt denselben
> Auftrag noch einmal los, und der Eintrag liegt danach doppelt in der Liste. Sperren
> wir den Knopf nach dem ersten Klick, ist der sichtbare Fehler weg, ein doppelter
> Auftrag aus einer zweiten Lasche aber weiterhin möglich. Sauber ist, dass zusätzlich
> der Server den wiederholten Auftrag erkennt und nichts doppelt anlegt; das kostet
> einen kleinen Server-Umbau. Welchen Weg nehmen wir?

Dieselbe Information, ein Durchgang zu lesen: der Ablauf steht als Ablauf da, die
Optionen hängen als ganze Sätze daran, und der Dateiname bleibt draussen, weil er zum
Entscheiden nichts beiträgt.

---

## Modus B (Rückfall): sequenziell, ohne Arbeiter

Für Werkzeuge ohne Subagenten. Die Parallelität entfällt, die Disziplin bleibt:

- Ein Task nach dem anderen, in der Reihenfolge der Wellen, alle offenen Tasks am Stück.
  Angehalten wird nur aus den zwei Gründen in „Am Stück bis zum Ende"; in Modus B ist
  „Kontext voll" dein eigener Kontext.
- Je Task: Test schreiben → rot laufen lassen und die Ausgabe festhalten → implementieren
  bis grün → sofort abhaken → Commit.
- Fragen sammeln und am Ende gebündelt stellen, nicht mittendrin.
- Der Gegenleser aus der Plan-Phase wird zum bewussten Rollenwechsel im selben Chat.

**Ehrlich gesagt:** Modus B ist schwächer. Kein frischer Kontext pro Task, also läuft der
Chat mit der Zeit voll; und Selbstkritik ersetzt keinen echten Zweitleser. Modus B ist
der Rückfall, nicht die Empfehlung.

---

## Ausbaustufe 1 — leichtes Review nach dem Bau

Wenn alle Tasks stehen, kann ein Lese-Arbeiter einmal über den Gesamt-Unterschied gehen,
mit dieser Checkliste: tote Pfade (Code, den nichts aufruft), vergessene Fehlerfälle,
Duplikate zu bereits Bestehendem. Eine Runde, Ergebnis als nummerierte Liste, kein
zweiter Durchgang. Das ist das zweite Augenpaar auf das Ganze, das die Task-Sicht nicht
hat. Für ein kleines Feature ist es Aufwand ohne Ertrag, dann weglassen.

## Ausbaustufe 2 — Mitschreib-Datei bei langen Läufen

Ein Arbeiter mit langem Auftrag schreibt seinen Stand fortlaufend nach
`<AGENTENORDNER>/state/<slug>-mitschrieb.md`: erledigte Teilschritte, Befunde mit
`Pfad:Zeile`, „wo ich gerade stehe", nach jedem Teilschritt, nicht erst am Ende. Bricht
er ab, liest ein frischer Arbeiter die Datei und macht beim ersten offenen Punkt weiter,
statt die Arbeit zu wiederholen. Bei kurzen Features unnötig.

Dieselbe Datei ist der Eingang, wenn ein Arbeiter an der Budget-Grenze von etwa 120 000
Tokens übergibt: sein Stand-Brief plus die Mitschreib-Datei gehen an einen frischen
Arbeiter, nie an den alten als Fortsetzung.

Die Mitschreib-Datei ist die **untere** Hälfte des Kontext-Haushalts: sie rettet den
Stand **eines** Arbeiters. Die obere Hälfte — was passiert, wenn der Hauptkontext des
Orchestrators voll wird — steht in `<AGENTENORDNER>/vorgehen/04-kontext.md`, samt
Handoff-Zyklus, Arbeiter-Budget und Budget-Sensor.
