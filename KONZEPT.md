# KONZEPT — scratchpad als vorführbares Hands-on-Harness

Stand: 2026-08-17. Dieses Dokument ist die Bau-Grundlage; es wird von einem
Prüf-Agenten gegengelesen. Quellen: `agent1-polier-sync-ledger.md` (was aus
curaops nach polier übernommen bzw. abgebaut wurde und warum) und
`agent2-curaops-on-polier-proposal.md` (Divergenz-Inventur + Schalter-Konzept),
beide im Session-Scratchpad.

## Ziel und Nicht-Ziel

**Ziel:** Ein scharf geschnittenes Demo-Harness, mit dem sich **Context
Engineering und Qualitätssicherung** vorführen lassen — nicht der volle
curaops-Funktionsumfang. Jedes Teil des Repos muss eine der vier Demo-Thesen
untermauern:

1. **Absicht vor Plan vor Code** (drei Phasen, harte Übergabepunkte).
2. **Kontext ist die knappe Ressource** (Orchestrator/Arbeiter-Trennung,
   Verdichtung, Budget, Handoff).
3. **Qualität ist erzwingbar, nicht erhofft** (TDD rot→grün, adversariales
   Gegenlesen, deterministische Wächter).
4. **Intelligenz gehört ins Modell, Determinismus in die Hooks** (die zentrale
   Design-Linie, siehe Kern-Entscheidung 3).

**Nicht-Ziel:** Stack-Bindung (Gradle/Playwright/Sonar), Telemetrie-Ketten,
Antwortform-Durchsetzung per Hook, Multi-Command-Kataloge. Alles, was in der
Demo nicht in 30 Minuten zeigbar ist, fliegt raus.

## Die drei Phasen (bleiben, werden geschärft)

Der Alt-Bestand `kern/01..03` ist strukturell richtig und bleibt Basis:

- **01-brainstorm** — sokratisches Absichts-Gate, Ergebnis: 6-Zeilen-Brief.
  Unverändert (ist bereits scharf).
- **02-plan** — Brief → Entwurf → **adversarialer Gegenleser** (Pflicht, eigener
  Arbeiter mit frischem Kontext) → Konsens-Runde (max. 2) → Drei-Zonen-Plan mit
  atomaren Tasks. NEU sichtbar: **Modell-Routing** — Entwurf UND Gegenleser
  laufen auf dem teuren Modell (`model: opus`), weil hier Urteilskraft zählt;
  der Gegenleser bekommt NUR den Entwurf, nie den Autor-Kontext (sonst liest er
  wohlwollend mit statt adversarial).
- **03-build** — Orchestrator dispatcht Arbeiter pro Task (test-first-Vertrag,
  Rot-Beleg-Pflicht, Rückgabe-Schema). NEU: Abschnitt **„Schleife oder
  Arbeiter"** (Ralph-Loop-Entscheidung, s.u.) und Verweis auf den
  Kontext-Haushalt (04). Modell-Routing: mechanische, exakt spezifizierte Tasks
  dürfen auf das günstigere Modell (`model: sonnet`), alles mit
  Interpretationsspielraum bleibt auf `opus` — nach unten nur bei garantiert
  identischem Output, nach oben nie automatisch.
- **NEU 04-kontext** — der Kontext-Haushalt als eigene Kern-Datei: warum ein
  voller Kontext teuer UND schlechter wird, Mitschrieb-Datei, Handoff-Brief,
  `/handoff` + `/clear` + `/resume`, und der Auto-Schalter (s.u.). Das ist die
  Context-Engineering-Vorzeigedatei der Demo.

## Kern-Entscheidung 1 — Ralph-Loop vs. Agenten-Dispatch

**Ein Ralph-Loop (selbst-wiederholender Lauf desselben Auftrags) ergibt genau
dann Sinn, wenn drei Bedingungen zusammen erfüllt sind:**

1. **Deterministisches, extern messbares Fertig-Kriterium** — Tests grün, Lint
   leer, oder „N saubere Review-Runden in Folge". Das Kriterium liegt außerhalb
   des Modells; der Loop kann sich nicht selbst für fertig erklären.
2. **Jede Runde startet mit frischem Kontext** — der gesamte Zustand (Streak,
   Findings, Runden-Zähler) liegt in Dateien, nicht im Chatverlauf. Genau das
   macht den Loop billig: kein wachsender Kontext über Runden.
3. **Konvergenz wird überwacht** — Runden-Obergrenze plus Pendel-Erkennung
   (dieselbe Stelle wird zum zweiten Mal „gefixt" → abbrechen und parken, statt
   endlos hin- und herzupendeln).

**Agenten-Dispatch ist besser**, wenn die Arbeit in **einmalige, disjunkte
Tasks** zerfällt (Plan-Abarbeitung): jeder Task hat eigenen Scope, eigene
Akzeptanzkriterien, und ist danach FERTIG — es gibt nichts zu wiederholen.
Kurzformel für die Demo: **Dispatch für Erzeugen, Loop für Konvergieren.**
Beleg aus der Praxis: polier `deep-check-loop` (Review→Fix bis 2 saubere Runden
in Folge, mit Pendel-Wächter — `C:\source\polier\commands\deep-check-loop.md`)
vs. `build` (Wellen disjunkter Tasks).

**Demo-Artefakt:** neues Command `agent/commands/loop.md` — Review→Fix-Schleife
über den aktuellen Diff bis 2 saubere Runden in Folge, max. 6 Runden, Zustand in
`<AGENTENORDNER>/state/loop-stand.md`, Pendel-Regel, geparkte Streitfälle als
Daten zurück an den User. Bewusst 2er-Streak (nicht 4): polier hat den Streak
selbst von 4 auf 2 gesenkt (agent1-Ledger WU3a) — mehr Runden kaufen kaum
Findings für viel Geld.

## Kern-Entscheidung 2 — Auto-Handoff: JA, mit explizitem Schalter, Default AUS

**Gehört in die Demo**, weil es das schärfste Context-Engineering-Exponat ist:
ein deterministischer Sensor misst am Turn-Ende den echten Kontextstand aus dem
Transcript und reagiert, BEVOR die Session unbrauchbar wird.

**Mechanik** (Port von `C:\source\polier\hooks\guard_context_budget.py`,
seinerseits aus curaops nachgezogen, Schwelle dort 150k):

- Stop-Hook `hooks/guard_context_budget.py`, misst den letzten `usage`-Block des
  Transcripts (Input + Cache-Read + Cache-Write).
- **Default (Schalter aus): warnen.** Über der Schwelle meldet der Hook einmalig
  pro Session: „Kontext bei ~Xk — jetzt `/handoff`, dann `/clear` + `/resume`."
  Der User entscheidet. Kein Block, keine Wiederholung pro Turn (Stempel-Datei).
- **`auto`-Schalter an (`SCRATCHPAD_AUTO_HANDOFF=1`): erzwingen.** Der Hook
  beendet den Turn mit exit 2 und der Auflage, JETZT den Handoff-Brief nach
  `<AGENTENORDNER>/state/handoff-brief.md` zu schreiben. `/clear` + `/resume`
  bleiben Handarbeit — das kann ein Hook technisch nicht auslösen, und das
  sagen wir in der Demo ehrlich dazu (Grenze des Werkzeugs, kein Bug).
- Schwelle per `SCRATCHPAD_KONTEXT_BUDGET` überschreibbar (Default 150000;
  kaputter Wert → Default). Für die Demo lässt sich die Schwelle damit auf
  z.B. 20k senken und der Handoff live vorführen — der eigentliche Grund,
  warum der Schalter ein ENV ist und keine Config-Datei: eine Zeile im
  Terminal, sofort wirksam, nichts zu editieren.

**Warum Default AUS:** Der User will nicht, dass das immer selbsttätig passiert
(explizite Vorgabe). Ein erzwungener Handoff mitten in einer Diskussion ist
Bevormundung; die Warnung liefert dieselbe Information ohne Kontrollverlust.
`auto` ist die Opt-in-Stufe für lange unbeaufsichtigte Läufe.

**Neue Commands dazu:** `handoff.md` (destillierter Stand → Brief-Datei, an
sauberem Übergabepunkt) und `resume.md` (Brief lesen, GEGEN den Arbeitsbaum
verifizieren — der Brief kann stale sein —, dann weitermachen). Vorlage:
`C:\source\polier\commands\handoff.md` / `resume.md`, radikal gekürzt.

## Kern-Entscheidung 3 — „intelligente Erkennung" durch das Harness: NEIN (mit einer präzisen Ausnahme)

Soll das Harness **selbst erkennen**, wo Ralph-Loop vs. Dispatch vs.
Auto-Handoff dran ist? **Nein — mit genau einer Ausnahme.**

- **Loop vs. Dispatch ist eine Urteils-Frage** (Zerfällt die Arbeit in
  disjunkte Tasks? Gibt es ein externes Fertig-Kriterium?). Urteil gehört ins
  Modell, als Entscheidungsregel in Prosa (Abschnitt in 03-build) — nicht in
  einen Hook. Der Beleg, dass heuristische „schlaue" Wächter scheitern, steht
  im agent1-Ledger: `guard_dispatch_nudge` und `guard_subagent_tokens` wurden
  in polier GELÖSCHT (Rausch), `guard_plan_drift` produzierte **434 von 436
  Warnungen als Fehlalarm** und wurde auf einen einzigen deterministischen
  Verdacht verengt. Heuristik im Hook = Rauschen, das der User wegklickt und
  dann auch die echten Treffer ignoriert.
- **Die Ausnahme: was deterministisch messbar ist, darf das Harness erkennen.**
  Kontextgröße ist eine Zahl im Transcript — deshalb ist Auto-Handoff (Kern-
  Entscheidung 2) als Sensor legitim, mit Schalter für die Reaktionsstufe.
- Demo-Merksatz: **„Das Harness misst, das Modell urteilt, der User
  entscheidet."** Genau in dieser Reihenfolge.

## Kern-Entscheidung 4 — der Treiber: ein Prozess AUSSERHALB der Sitzung fährt den Handoff-Zyklus

Kern-Entscheidung 2 endet an einer ehrlichen Grenze: ein Wächter kann `/clear`
und `/resume` nicht auslösen — das sind Befehle des Programms selbst. Für lange
unbeaufsichtigte Läufe (der User geht stundenweise weg) schließt `treiber.py`
diese Lücke: ein kleines Python-Skript **außerhalb der Sitzung**, das den ganzen
Zyklus selbst fährt.

**Mechanik (synchroner Loop, bewusst KEINE Staffel):**

1. `python treiber.py auto "<auftrag>"` startet eine headless Sitzung
   (`claude -p … --dangerously-skip-permissions`) mit dem Auftrag plus
   Treiber-Vertrag, und mit `SCRATCHPAD_AUTO_HANDOFF=1` in der Umgebung.
2. Läuft die Sitzung an die Kontext-Grenze, erzwingt `guard_context_budget` den
   Handoff-Brief; die Sitzung schreibt ihn und beendet ihren Turn → der
   `claude`-Prozess endet. Der Treiber (der synchron wartet) sieht das Ende.
3. Der Treiber startet **sofort eine frische Sitzung** mit dem Resume-Auftrag
   („lies `state/handoff-brief.md`, prüfe gegen den Arbeitsbaum, mach beim
   ersten offenen Punkt weiter") — der Inhalt von `/resume` als Prompt.
4. Das wiederholt sich, bis ein Ende-Signal greift.

**Ende-Erkennung — nur Dateien und Exit-Codes, nichts Geratenes:**

| Signal | Bedeutung |
|---|---|
| `state/treiber-fertig` existiert | die Sitzung meldet: Auftrag fertig (oder nur noch User-Entscheidungen offen). Sauberes Ende. |
| `state/treiber-stopp` existiert | Not-Aus durch den Menschen (`python treiber.py stopp` oder Datei anlegen). Greift vor jeder neuen Runde. |
| Brief-Hash zweimal in Folge unverändert | Stillstand — die Runden produzieren nichts mehr. Abbruch. |
| Sitzungs-Exit ≠ 0, zweimal in Folge | Fehler (Login, Netz, CLI). Abbruch. |
| Runden-Obergrenze (Default 40, `--max-runden`) | Kosten-Deckel. Abbruch mit Bericht. |

Dazu Strg+C im Treiber-Fenster (der Loop läuft im Vordergrund). Anders als das
curaops-Vorbild (`scripts/autopilot.py`: Staffel ohne Limit, die Sitzung ruft
`--next` selbst und wird detached neu gestartet) behält der Treiber hier ein
Default-Limit: ein Demo-Harness, das mit abgeschalteten Freigaben unbegrenzt
läuft, ist das falsche Exponat.

**Warum synchroner Loop statt Staffel:** die Staffel braucht Detach-Mechanik,
PID-Ahnen-Prüfung und einen Selbstaufruf aus der Sitzung heraus (curaops
`autopilot.py:250-282`). Der synchrone Loop braucht nichts davon: ein Prozess,
ein Fenster, `subprocess` wartet. Für die Demo ist der einfachere Mechanismus
der bessere — und er beantwortet nebenbei die Fenster-Frage: **es gibt nie ein
altes Fenster zu schließen**, weil alle Sitzungen headless nacheinander im
einen Treiber-Fenster laufen. Ein „neues Fenster pro Runde + altes schließen"
wäre auf Windows nur per Prozess-Kill des alten Fensters machbar — mit dem
Risiko, eine Sitzung mitten im Brief-Schreiben zu töten. Deshalb: bewusst ein
Fenster, kein Schalter nötig.

**Sicherheits-Preis, ehrlich benannt:** `--dangerously-skip-permissions` ist
Voraussetzung — eine unbeaufsichtigte Sitzung kann keine Freigabe-Fragen
beantworten, und Schreiben unter den Agenten-Ordner gilt als „sensitive file",
was auch Allow-Regeln nicht aufheben (in curaops gemessen, `autopilot.py:201-210`).
Die Sitzung darf damit ALLES, was das Konto darf. Gegenmittel im README:
nur in Wegwerf-/Branch-Umgebungen fahren, Runden-Limit, Not-Aus-Datei,
kein `git push` im Vertrag.

Der Wächter `guard_context_budget` bekommt dafür genau EINE Ergänzung: existiert
der Marker `state/treiber-aktiv` (legt der Treiber an, räumt er weg), nennt die
Auto-Meldung den Treiber-Weg („Brief schreiben, Turn beenden — der Treiber
startet die nächste Runde") statt der Handarbeit `/clear` + `/resume`. Geprüft
wird nur die Existenz der Datei — Schwelle, Messung und fail-open bleiben
unverändert (gleiches Muster wie die Autopilot-Ausnahme in curaops).

## Kern-Entscheidung 5 — Treiber vs. Ralph-Loop, und wer den Modus wählt

Der Treiber und die Schleife (`/loop`) sehen sich ähnlich (beides „wiederholen,
bis fertig") und sind es nicht. Die Kriterien:

| Kriterium | Ralph-Loop (`/loop`) | Treiber (`treiber.py auto`) |
|---|---|---|
| Fertig-Kriterium | **extern messbar** (null Befunde, 2 saubere Runden, Tests grün) | **nicht messbar** — „Auftrag fertig" ist ein Urteil der Sitzung |
| Art der Arbeit | **Konvergieren**: denselben Stand nachschärfen | **Erzeugen**: neuen Stand aufbauen (Plan abarbeiten, Feature bauen) |
| Zustand lebt in | kleiner Zustands-Datei (`loop-stand.md`), jede Runde liest NUR sie | Arbeitsbaum + Brief; der Brief muss den ganzen Kopf-Stand destillieren |
| Kontext pro Runde | klein und konstant (das macht den Loop billig) | wächst pro Runde bis zur Budget-Grenze, dann Schnitt |
| Beaufsichtigung | im Gespräch, User sitzt daneben | ausdrücklich unbeaufsichtigt, Freigaben abgeschaltet |
| Divergenz-Schutz | Pendel-Regel + Obergrenze | Stillstand-Erkennung + Obergrenze + Not-Aus-Datei |
| Typischer Fall | Diff nachschärfen, Lint/Review leerlaufen lassen | stundenlange Bau-Arbeit über viele Kontexte hinweg |

Kurzformel, Fortschreibung von Kern-Entscheidung 1: **Dispatch für Erzeugen,
Loop für Konvergieren — und der Treiber, wenn das Erzeugen länger dauert als
ein Kontext reicht.** Der Treiber ersetzt den Loop nicht: eine
Konvergenz-Aufgabe im Treiber wäre Verschwendung (jede Runde schleppt
Bau-Kontext bis zur Grenze, obwohl eine kleine Zustands-Datei reichte). Ein
Loop ersetzt den Treiber nicht: ohne messbares Fertig-Kriterium weiß ein Loop
nie, wann er aufhören darf, und an der Kontext-Grenze bräuchte er trotzdem
einen Menschen für `/clear` + `/resume`.

**Wer wählt den Modus — Mensch oder Treiber? Vorlage für die User-Entscheidung:**

- **Variante A — der Mensch wählt vor dem Start.** Pro: die Frage „zerfällt die
  Arbeit in Konvergenz oder Erzeugung?" ist eine Urteils-Frage, und
  Kern-Entscheidung 3 legt fest, dass Urteil nicht ins Harness gehört; ein
  Fehlgriff der Automatik liefe stundenlang unbeaufsichtigt in die falsche
  Richtung. Contra: der User muss die Unterscheidung kennen (eine Zeile Doku).
- **Variante B — der Treiber entscheidet anhand der Auftrags-Art.** Pro: ein
  Kommando weniger. Contra: die Erkennung wäre Heuristik über Prosa-Aufträge —
  genau die Sorte „schlauer Wächter", die in polier als Rausch gelöscht wurde
  (434/436 Fehlalarme bei `guard_plan_drift` alt). Falls doch gewünscht, wären
  die Regeln: messbares Fertig-Kriterium im Auftrag benennbar („bis Tests
  grün", „bis Review leer") **und** Scope = bestehender Diff → Loop; sonst
  Treiber. Schon das erste Kriterium ist Text-Deutung, nicht Messung.
- **Empfehlung: Variante A.** Der Mensch wählt; die Entscheidungsregel steht
  als Prosa in dieser Tabelle und in `kern/04-kontext.md`. Das ist dieselbe
  Linie wie beim Auto-Handoff: das Harness misst (Kontextstand, Brief-Hash,
  Exit-Codes), das Modell urteilt (wann ist der Auftrag fertig), der User
  entscheidet (welcher Modus, wann Not-Aus).

## Wächter-Auswahl: vier, je einer pro Demo-These

| Wächter | Event | These | Disposition |
|---|---|---|---|
| `guard_tdd.py` | Stop | Qualität: Logik ohne Test endet nicht | bleibt (vorhanden) |
| `guard_test_quality.py` | PostToolUse Edit/Write | Qualität: Test, der nie rot werden kann, wird abgefangen | bleibt (vorhanden) |
| `guard_plan_drift.py` | Stop | Plan-Integrität: still verschwundene Task-Zeile | **verengen** auf polier-Stand (`C:\source\polier\hooks\guard_plan_drift.py`, 225 Z. statt 559er-Altmodell) — der Alt-Algorithmus im scratchpad ist die 434/436-Fehlalarm-Fassung |
| `guard_context_budget.py` | Stop | Kontext: Budget-Sensor + Auto-Handoff-Schalter | **NEU** (Port polier, plus Warn-Default/`SCRATCHPAD_AUTO_HANDOFF`) |

**Fliegt raus (mit Begründung, analog polier-Abbau):**

- `guard_answer_nudge.py` — Antwortform ist Stil-, nicht Substanz-Durchsetzung;
  in polier läuft die Antwortform-Strecke als Telemetrie, nicht als Zwang. Für
  die Demo Rausch. (Die Prosa `kern/antwortform.md` bleibt — das Frage-Gate mit
  Übersetzung in 03-build ist ein starkes Demo-Stück; nur der Hook geht.)
- `block_git_push.py`, `guard_git_revert.py` — Git-Hygiene, untermauert keine
  der vier Thesen. Die Regel „kein push" bleibt als Satz in 03-build.

Ergebnis: 4 Wächter, 4 Thesen, null Rausch-Wächter. `settings-hooks.json` wird
entsprechend verdrahtet (answer_nudge/git-Zeilen raus, context_budget auf Stop
dazu). Der `outputStyle`-Eintrag bleibt: der Antwortform-Hook fällt weg, das
Artefakt nicht — `kern/antwortform.md` wird beim Installieren zu
`<AGENTENORDNER>/output-styles/scratchpad-projektleiter.md`, und ein Style wirkt
nur, wenn er als Datei liegt UND in den Settings steht. Der Name trägt das
Präfix `scratchpad-`, damit er nicht mit einem gleichnamigen Style des
Zielprojekts kollidiert. Eingetragen wird er per JSON-Merge (`install_settings.py`),
nicht per String-Splice — und aus demselben Grund gilt das für den ganzen
Settings-Schritt: eine vorhandene `settings.json` des Zielprojekts wird ergänzt,
nie überschrieben.

## Modell-Routing (These „Planung mit höherwertigen Modellen")

Sichtbar an drei Stellen verankert:

1. `kern/rollen.md`: neuer Abschnitt „Welches Modell für welche Rolle" —
   Planung/Gegenlesen/Review = teures Modell (Urteilskraft), mechanische
   Umsetzung nach exakter Vorgabe = günstiges Modell (nur wenn der Output
   vorher exakt feststeht), nach oben nie automatisch eskalieren.
2. `02-plan.md`: Entwurf + Gegenleser explizit `model: opus` im Dispatch.
3. `03-build.md`: Arbeiter-Auftrag nennt das Modell pro Task; Default opus,
   Ausnahme-Kriterium für sonnet wörtlich („Output exakt bekannt, null
   Design-Entscheidungen").

## Datei-Disposition (Schreib-Scope: nur `C:\source\scratchpad`)

**Bleibt (ggf. geschärft):** `kern/01-brainstorm.md` · `kern/02-plan.md` (+
Modell-Routing) · `kern/03-build.md` (+ „Schleife oder Arbeiter", − Rollen-
Command-Verweise) · `kern/antwortform.md` · `kern/rollen.md` (+ Modell-Routing)
· `kern/rueckgabe-schema.md` · `kern/task-format.md` · `vorlagen/*` ·
`agent/commands/{brainstorm,plan,build}.md` · `agent/skills/grill-me/` ·
`agent/AGENTS-block.md` (aktualisieren) · `hooks/{guard_tdd,guard_test_quality,
hook_util}.py` + Tests · `.gitignore` · `README.md` (Neuschrieb als
Demo-Drehbuch).

**Neu:** `KONZEPT.md` (dieses Dokument) · `kern/04-kontext.md` ·
`agent/commands/{loop,handoff,resume}.md` · `hooks/guard_context_budget.py` +
`hooks/test_guard_context_budget.py` (TDD rot→grün) · `treiber.py` +
`test_treiber.py` (Kern-Entscheidung 4, TDD rot→grün; der Wächter bekommt dafür
den Treiber-Marker-Zweig).

**Verworfen: eine selbst startende Nachfolge-Sitzung.** Erwogen war ein
`rollover`-Command samt Starter-Skript, das an der Kontext-Grenze von sich aus
ein NEUES Fenster mit der Nachfolge-Sitzung aufmacht — der Fall zwischen
Handbetrieb und Treiber: ein Mensch sitzt davor, tippt aber nichts. Das ist
raus. Gründe: (1) das Fenster-Aufmachen ist reine Terminal-Akrobatik pro
Betriebssystem und belegt keine der vier Demo-Thesen; (2) eine Zusammenfassung
aus einem schon vollen Kontext erbt dessen Lücken — der Nachfolger startete mit
einem sauber formatierten Irrtum, und niemand sähe es; (3) es widerspricht der
Linie von Kern-Entscheidung 2 (Default warnen, der User entscheidet). Der
Übergabe-Weg ist darum durchgehend der Handbetrieb: die Sitzung meldet die
Grenze (`guard_context_budget.py`), der Mensch tippt `/handoff`, dann `/clear`,
dann `/resume`. Dass ein Hook `/clear` technisch nicht selbst auslösen kann,
sagen wir in der Demo ehrlich dazu — Grenze des Werkzeugs, kein Bug.

**Ersetzt:** `hooks/guard_plan_drift.py` + Test (verengtes Modell) ·
`agent/settings-hooks.json` · `install.ps1`/`install.sh` (je ~35k → je ein
kleines Kopier-Skript mit `<AGENTENORDNER>`-Ersetzung + Smoke-Test).

**Gelöscht:** `hooks/{guard_answer_nudge,block_git_push,guard_git_revert}.py`
+ zugehörige Tests · `hooks/__pycache__/` · `agent/commands/{backend,frontend,
fullstack,ref}.md` (Stack-Rollen: Projekt-Flavor, keine Demo-These) ·
`install.mjs` · `package.json` · `pruefe-gleichstand.sh` (Gleichstands-Prüfung
gegen polier ist für ein Demo-Repo gegenstandslos).

## Bau-Regeln

TDD für alles Ausführbare: erst roter Test, dann Code, Rot-Beleg in die
Rückgabe. Kein Commit. Zwei Bau-Agenten mit disjunkten Scopes: Agent A =
`hooks/` + `agent/settings-hooks.json`; Agent B = Prosa/Commands/README/
Installer. Verifikation am Ende: kompletter Hook-Testlauf + Installer-Smoke-Test.
