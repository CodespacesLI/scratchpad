# scratchpad — ein Hands-on-Harness zum Vorfuehren

Ein kleines, scharf geschnittenes Vorgehen fuer die Arbeit mit einem
KI-Programmierwerkzeug: drei Phasen, sechs Kurzbefehle, vier Waechter. Gebaut, um in
etwa 30 Minuten **vorgefuehrt** zu werden.

**Das hier ist nicht das volle Arbeits-Harness.** Alles, was sich nicht live zeigen
laesst, ist absichtlich draussen: keine Stack-Bindung, keine Telemetrie-Ketten, kein
Befehls-Katalog. Jedes Teil im Repo untermauert genau eine von vier Thesen:

1. **Absicht vor Plan vor Code.** Drei Phasen mit harten Uebergabepunkten.
2. **Kontext ist die knappe Ressource.** Trennen, verdichten, uebergeben.
3. **Qualitaet ist erzwingbar, nicht erhofft.** Test zuerst, adversariales Gegenlesen,
   deterministische Waechter.
4. **Intelligenz gehoert ins Modell, Determinismus in die Hooks.** Ein Waechter misst,
   er raet nicht.

Die Begruendungen hinter jeder Entscheidung stehen in `KONZEPT.md`. Dieses README ist
das Drehbuch fuer die Vorfuehrung.

**Das Repo laeuft nicht selbst.** Es ist eine Sammlung von Anleitungstexten und vier
kleinen Pruefprogrammen, die per Installer in *ein Projekt* kopiert werden. Du klonst es
einmal, installierst es in ein Projekt, und arbeitest ab dann dort.

---

## Einrichtung — ein Befehl

```
git clone https://github.com/<user>/scratchpad C:\source\scratchpad

pwsh -File C:\source\scratchpad\install.ps1 C:\projekte\merkliste   # fragt nach dem Modus
bash /c/source/scratchpad/install.sh ~/projekte/merkliste             # fragt nach dem Modus
```

Das zweite Argument ist optional und automatisiert die Auswahl:

```
pwsh -File C:\source\scratchpad\install.ps1 C:\projekte\merkliste codex
bash /c/source/scratchpad/install.sh ~/projekte/merkliste claude
```

| Modus | Installiert |
|---|---|
| `neutral` | Nur den toolneutralen Kern unter `.agents/`: `vorgehen/`, `tasks/README.md` und `INSTRUCTIONS.md`. |
| `codex` | Den neutralen Kern plus `.agents/skills/` und einen klar markierten, idempotenten Scratchpad-Block in `AGENTS.md`; vorhandener Inhalt bleibt erhalten. |
| `claude` | Die bisherige Claude-Code-Integration unter `.claude/`: Commands, Skills, Hooks, Output-Style und gemergte `settings.json`. |

Der Claude-Modus ergibt im Projekt:

```
merkliste/
  .claude/
    vorgehen/         die Anleitungstexte (aus kern/)
    commands/         die sechs Kurzbefehle
    skills/           der Selbststarter fuer Phase 1
    hooks/            die vier Waechter
    output-styles/    die Antwortform als scratchpad-projektleiter.md
    settings.json     verdrahtet die Waechter, traegt den Output-Style ein
    tasks/
      README.md       hier kommen die Plaene rein
```

Der Output-Style heisst bewusst `scratchpad-projektleiter` und nicht `projektleiter`:
der Installer traegt ihn als `"outputStyle": "scratchpad-projektleiter"` in die
`settings.json` ein, und ein gleichnamiger eigener Style des Nutzers wuerde sonst bei
jeder Schulungsinstallation still ueberschrieben.

Der Installer ist idempotent: derselbe Befehl noch einmal aktualisiert sauber. Beide
Fassungen tun dasselbe; `bash test_install.sh` prueft alle drei Modi und die
Bash/PowerShell-Paritaet nach. **Aenderungen gehoeren
in den Klon**, nie in die kopierte Fassung im Projekt — der naechste Lauf ueberschreibt
sie kommentarlos.

---

## Der Walkthrough — vom leeren Ordner zur Merkliste

### 1. Absicht klaeren — `/brainstorm`

```
/brainstorm ich will eine Merkliste fuer Sachen, die ich spaeter lesen will
```

Die KI baut nichts, sondern stellt nummerierte Fragen, zwei bis vier pro Runde: Wer
nutzt das? Was machst du heute stattdessen? Was ist die *eine* Sache, die drin sein
muss? Sie hakt nach, wo du ausweichst, und verlangt mindestens ein **Nicht-Ziel**.

**Ergebnis:** ein Brief aus sechs Zeilen (Zweck, Kern, Nicht-Ziel, Ablauf, Randfaelle,
Erfolg). Kein Code, keine Datei: ein Text, auf den sich ab jetzt beide berufen.

**Der Moment fuer die Vorfuehrung:** die erste Frage, die dem Zuschauer selbst noch
nicht klar war. Genau dort haette die KI sonst geraten und gebaut.

### 2. Plan schneiden — `/plan`

```
/plan
```

Die KI durchsucht erst das Projekt nach Bausteinen, die schon da sind
(Wiederverwenden schlaegt neu bauen). Dann schreibt sie einen Entwurf und gibt ihn an
einen **zweiten Arbeiter mit frischem Kontext**, der ihn zerreissen soll: zu viel
gebaut, Randfaelle vergessen, Wiederverwendung verpasst, Schichten verletzt. Die
Einwaende arbeitet sie ein, maximal zwei Runden.

**Ergebnis:** `.claude/tasks/merkliste.md` mit `Status: entwurf` — fuenf Zeilen Kurzfassung, die
getroffenen und die offenen Entscheidungen, dann die Aufgabenliste. Jede Aufgabe ist
2–5 Minuten Arbeit und traegt Rolle, exakte Dateiliste, 1–3 Akzeptanzkriterien im Muster
„Wenn X, dann Y" und den zugehoerigen Test.

Hier stoppt die KI und wartet auf die Freigabe.

### 3. Plan bauen — `/build`

```
/build .claude/tasks/merkliste.md
```

Die KI wird zum Bauleiter und baut selbst nichts mehr. Sie setzt den Plan auf
`Status: im-bau`, prueft, welche Aufgaben gleichzeitig laufen koennen (Dateilisten
duerfen sich nicht ueberschneiden), und startet dafuer je einen Arbeiter. Jeder Arbeiter
bekommt genau eine Aufgabe, seine Dateiliste, sein Modell und die Ansage: erst den Test
schreiben, ihn einmal **rot** laufen lassen, dann bauen bis gruen.

Nach jeder Rueckmeldung prueft der Bauleiter nach — laeuft der Test wirklich, wurden nur
die erlaubten Dateien angefasst, liegt der Rot-Beleg vor — und setzt erst dann das
Haekchen im Plan.

**Ergebnis:** alle Haken gesetzt, `Status: fertig`, Plan nach `.claude/tasks/done/` (nie
geloescht), ein kurzer
Bericht und alle Rueckfragen **gebuendelt an einer Stelle** statt tropfenweise
zwischendurch.

### 4. Kontext haushalten — laeuft quer durch alle drei

`vorgehen/04-kontext.md` ist keine vierte Phase, sondern die Ressourcen-Rechnung:
warum ein voller Kontext teuer **und** schlechter wird, wie der Stand mitgeschrieben
wird, und wie der Zyklus `/handoff` → `/clear` → `/resume` eine lange Sitzung ueber die
Grenze rettet. Das ist das Herzstueck der Vorfuehrung, siehe unten.

Dieselbe Rechnung gilt **pro Arbeiter**: ueber ~120k Tokens hinaus bekommt keiner
Folgearbeit, er schliesst am naechsten Uebergabepunkt ab, gibt einen kompakten
Stand-Brief zurueck, und der Rest geht an einen frischen Arbeiter (Ausnahme: reine Test-
und Build-Auslaeufe duerfen auslaufen). Ausfuehrlich in `vorgehen/04-kontext.md`.

---

## Die vier Waechter — je einer pro These

Kleine Python-Programme, die bei bestimmten Ereignissen automatisch mitlaufen. **Keiner
von ihnen raet.** Was Urteil braucht, steht als Regel in Prosa; ein Waechter darf nur,
was sich deterministisch messen laesst.

| Waechter | These | Der vorfuehrbare Moment |
|---|---|---|
| `guard_tdd` | Logik ohne Test endet nicht | Eine Zeile Logik aendern, Zug beenden wollen — der Zug kommt als Nachbesserungs-Auftrag zurueck. |
| `guard_test_quality` | Ein Test, der nie rot werden kann, beweist nichts | Einen Test mit leerem Rumpf oder ohne Zusicherung schreiben — der Waechter meldet sich beim Speichern. |
| `guard_plan_drift` | Eine Aufgabe verschwindet nicht still aus dem Plan | Eine `- [ ]`-Zeile aus `.claude/tasks/merkliste.md` loeschen, ohne sie zu begruenden — er meldet genau diesen einen Fall. (Der Plan muss auf `Status: im-bau` oder `fertig` stehen; im Entwurf kommen und gehen Zeilen legitim.) |
| `guard_context_budget` | Kontextgroesse ist messbar, also darf das Harness sie messen | Schwelle absenken, weiterarbeiten — die Warnung kommt einmalig, mit dem Schalter stattdessen der erzwungene Brief. |

**Warum nur vier.** Frueher standen hier mehr. Wer heuristisch raet, produziert
Fehlalarme; der Nutzer klickt sie weg und uebersieht danach auch die echten Treffer.
Belegt in `KONZEPT.md`: ein Waechter lag in **434 von 436 Faellen** falsch und wurde auf
einen einzigen deterministischen Verdacht verengt. Deshalb ist `guard_plan_drift` heute
still, ausser bei der unbegruendet verschwundenen Task-Zeile.

Waechter laufen nur in Werkzeugen, die Hooks unterstuetzen. Ueber `AGENTS.md` allein
gibt es sie nicht; dort sind die Regeln reine Selbstdisziplin — und das steht auch so im
Textblock (`agent/AGENTS-block.md`).

---

## Vorfuehr-Kapitel

Vier Stuecke, jedes einzeln zeigbar, zusammen etwa 25 Minuten.

### (a) Der Kontext-Sensor, live — das Kernstueck

Der Waechter misst am Zugende den echten Kontextstand aus dem Sitzungsprotokoll. Damit
das nicht erst nach zwei Stunden passiert, wird die Schwelle fuer die Vorfuehrung
abgesenkt — **eine Zeile im Terminal, sofort wirksam, nichts zu editieren.** Genau
deshalb ist der Schalter eine Umgebungsvariable und keine Konfigurationsdatei.

**Schritt 1 — die Warnung provozieren:**

```
SCRATCHPAD_KONTEXT_BUDGET=20000 claude                 # Mac/Linux
$env:SCRATCHPAD_KONTEXT_BUDGET='20000'; claude         # Windows (PowerShell)
```

Ein paar Zuege arbeiten, bis 20k ueberschritten sind. Dann meldet sich der Waechter
**einmal**: „Kontext bei ~Xk — jetzt `/handoff`, dann `/clear` + `/resume`." Er blockt
nichts und wiederholt sich nicht.

**Schritt 2 — den Zwang zeigen:**

```
SCRATCHPAD_KONTEXT_BUDGET=20000 SCRATCHPAD_AUTO_HANDOFF=1 claude          # Mac/Linux
$env:SCRATCHPAD_KONTEXT_BUDGET='20000'; $env:SCRATCHPAD_AUTO_HANDOFF='1'; claude   # Windows
```

Jetzt endet der Zug mit der Auflage, den Brief **sofort** zu schreiben. Danach liegt
`.claude/state/handoff-brief.md` auf der Platte — aufmachen und zeigen: eine Seite,
ERLEDIGT / OFFEN / WO ICH STEHE / BELEGE, keine Diffs, keine Nacherzaehlung.

**Schritt 3 — den Zyklus schliessen:** `/clear`, dann `/resume`. Die KI liest den Brief
und **prueft ihn gegen den Arbeitsbaum**, statt ihm zu glauben — Branch, letzter Commit,
Abhak-Stand im Plan, zwei Stichproben aus ERLEDIGT.

**Die Grenze ehrlich dazusagen:** `/clear` und `/resume` bleiben Handarbeit. Ein Hook
kann das Gespraech nicht leeren und keinen Befehl starten; er kann nur den Zug beenden
und eine Auflage mitgeben. Auch mit `AUTO_HANDOFF=1` ist nur der **Brief** automatisch.
Das ist eine Grenze des Werkzeugs, kein Fehler — und die Frage kommt aus dem Publikum
ohnehin. Deshalb gibt es auch keinen Kurzbefehl, der eine Nachfolge-Sitzung aufmacht: an
der Grenze **meldet** die Sitzung, dass jetzt `/handoff` faellig ist, und der Mensch tippt
danach `/clear` und `/resume`. Wer das unbeaufsichtigt braucht, nimmt den Treiber weiter
unten, der ausserhalb der Sitzung steht und deshalb darf, was ein Hook nicht kann.

**Default ist bewusst nur die Warnung.** Ein erzwungener Handoff mitten in einer
Diskussion ist Bevormundung; die Warnung liefert dieselbe Information ohne
Kontrollverlust. `AUTO_HANDOFF` ist die Opt-in-Stufe fuer lange unbeaufsichtigte Laeufe.

### (b) `/loop` auf einem kleinen Unterschied

```
/loop
```

Eine Runde ist: **Review-Arbeiter** (teures Modell, frischer Kontext) findet Maengel →
**Fix-Arbeiter** behebt sie test-first → naechste Runde gegen den neu berechneten
Unterschied. Eine Runde ist **sauber** bei null neuen Befunden; fertig ist die Schleife
nach **zwei sauberen Runden in Folge**, Obergrenze sechs.

Drei Dinge zeigen:

1. **Der Zustand steht in `.claude/state/loop-stand.md`**, nicht im Gespraech — deshalb
   startet jede Runde frisch und der Kontext waechst ueber die Runden **nicht** mit.
   Das ist der ganze Trick.
2. **Zwei saubere Runden, nicht eine.** Eine einzelne saubere Runde ist Zufall, keine
   Bestaetigung.
3. **Die Pendel-Regel.** Baut Runde 2 zurueck, was Runde 1 gebaut hat, ist das kein
   Mangel mehr, sondern ein Streitfall ohne eindeutige Antwort: sofort abbrechen und dem
   Nutzer beide Positionen vorlegen, statt endlos hin und her zu bauen.

Der Gegensatz zur Bau-Phase ist die eigentliche Lehre: **`/build` dispatcht** disjunkte
Aufgaben, die danach fertig sind; **`/loop` wiederholt** denselben Auftrag gegen ein
messbares Kriterium. Wann was gilt, steht in `vorgehen/03-build.md` unter „Vorfrage —
Schleife oder Arbeiter?".

### (c) Der Gegenleser in der Plan-Phase

In `/plan` wird der Entwurf **zweimal** angefasst: einmal vom Autor, einmal von einem
eigenen Arbeiter, der **nur den Entwurf bekommt** — nicht das Gespraech, nicht die
Fundstellen aus der Erkundung, nicht die Begruendungen des Autors.

Das ist der Punkt, den man vorfuehren muss: **wer die Begruendung schon kennt, liest
wohlwollend mit.** Er prueft dann, ob der Entwurf zur Begruendung passt, statt ob die
Begruendung traegt. Der frische Kontext ist der Wirkstoff, nicht die Pruefliste.

Zum Zeigen: die Einwaende des Gegenlesers auf den Tisch legen und fragen, welche davon
der Autor selbst gefunden haette. Erfahrungsgemaess sind es die zu-wenig-gebaut-Faelle —
fehlende Leerzustaende, fehlende Rechtepruefung —, die der Autor nie sieht, weil er
seinen eigenen Happy Path im Kopf hat.

### (d) Modell-Routing — wo teuer, wo guenstig, warum

Drei Regeln, sichtbar an drei Stellen verankert (`vorgehen/rollen.md`,
`vorgehen/02-plan.md`, `vorgehen/03-build.md`):

| Wo | Modell | Warum |
|---|---|---|
| Planen, Gegenlesen, jede Review-Runde | **teuer** | Hier entscheidet sich, ob das Richtige gebaut wird. Ein Denkfehler im Plan wird von jedem Arbeiter pflichtbewusst mitgebaut. |
| Vertrag, Logik, alles mit Interpretationsspielraum | **teuer** | Default. Im geringsten Zweifel bleibt die Aufgabe oben. |
| Mechanischer Umbau nach exakter Vorgabe | guenstig | Nur wenn der **Output vorher exakt bekannt** ist und **null Design-Entscheidungen** offen sind. |
| Eskalation nach oben | nie automatisch | Das teuerste Modell waehlt der Nutzer, nicht das Werkzeug. Laeuft eine Aufgabe heiss, wird sie **kleiner geschnitten**, nicht teurer besetzt. |

Die Pointe fuer das Publikum: **Am Denken wird nicht gespart, an der Mechanik schon.**
Die richtige Frage lautet nie „geht das billiger?", sondern „steht der Output vorher
exakt fest?".

---

## Der Treiber — stundenweise weggehen, ohne dass der Faden reisst

Der Budget-Sensor endet an einer ehrlichen Grenze: `/clear` und `/resume` kann kein
Waechter ausloesen. Fuer lange Bau-Arbeit ohne Menschen davor gibt es deshalb
`treiber.py` — ein Skript **ausserhalb der Sitzung**, das den ganzen Zyklus selbst
faehrt: Sitzung starten, an der Kontext-Grenze den Handoff-Brief erzwingen (der
Waechter laeuft mit `SCRATCHPAD_AUTO_HANDOFF=1`), das Sitzungs-Ende erkennen, sofort
eine frische Sitzung mit dem Brief starten — so oft, bis der Auftrag fertig ist.

```
python treiber.py auto "Arbeite .claude/tasks/mein-feature.md ab, Task fuer Task, test-first." --projekt C:\pfad\zum\projekt
python treiber.py status --projekt C:\pfad\zum\projekt     # eine Zeile Stand
python treiber.py stopp  --projekt C:\pfad\zum\projekt     # Not-Aus aus einem zweiten Terminal
```

**So endet ein Lauf** (nur Dateien und Exit-Codes, nichts Geratenes): die Sitzung legt
`state/treiber-fertig` an, wenn der Auftrag fertig ist · der Mensch legt
`state/treiber-stopp` an (oder `treiber.py stopp`, oder Strg+C im Treiber-Fenster) ·
zweimal in Folge keine Brief-Aenderung heisst Stillstand · zweimal Exit ungleich 0 in
Folge heisst Fehler · und es gibt eine Runden-Obergrenze (Default 40, `--max-runden`,
`0` = ausdruecklich unbegrenzt).

**Voraussetzungen:** das `claude`-CLI (angemeldet; ein gesetzter `ANTHROPIC_API_KEY`
wird entfernt, damit ueber das Abo abgerechnet wird), Python ab 3.9 — das ist schon da,
die Waechter brauchen dasselbe — und irgendeine Shell. Keine Zusatz-Pakete: nur
Standardbibliothek.

**Der Preis, unverschoent:** die Sitzungen laufen mit `--dangerously-skip-permissions`.
Sie fragen NIE nach — sie duerfen Dateien schreiben und loeschen, jedes Kommando
ausfuehren, ins Netz. Ein fehlgeleiteter Auftrag richtet also unbeaufsichtigt Schaden
an. Deshalb: nur auf einem eigenen Branch oder Worktree fahren, keine Produktiv-Zugaenge
in der Umgebung, Runden-Obergrenze dran lassen, und der Vertrag im Prompt verbietet
`git push`. Wer das nicht will, bleibt beim Handbetrieb aus `kern/04-kontext.md`.

**Warum kein Fenster-Wechsel:** der Treiber wartet synchron auf jede Sitzung; alle
Runden laufen headless nacheinander **im einen Treiber-Fenster**. Es gibt schlicht nie
ein altes Fenster zu schliessen — ein Fenster-pro-Runde-Modus wuerde auf Windows einen
Prozess-Kill des Vorgaengers brauchen, mit dem Risiko, eine Sitzung mitten im
Brief-Schreiben zu toeten. Begruendung: `KONZEPT.md`, Kern-Entscheidung 4.

**Treiber oder `/loop`?** Der Loop konvergiert (messbares Fertig-Kriterium, kleiner
Zustand in `loop-stand.md`), der Treiber erzeugt (kein messbares Kriterium, Zustand in
Arbeitsbaum + Brief) — Kriterien-Tabelle in `KONZEPT.md`, Kern-Entscheidung 5. Die Wahl
trifft der Mensch vor dem Start, nicht das Skript.

---

## Was im Repo liegt

| Ort | Inhalt |
|---|---|
| `kern/01-brainstorm.md` | Phase 1: Fragen-Runden, Abbruchregel, Brief-Format |
| `kern/02-plan.md` | Phase 2: Erkundung, Gegenleser, Konsens, Drei-Zonen-Plan |
| `kern/03-build.md` | Phase 3: Schleife oder Arbeiter, Wellen, Auftrag, pruefen, abhaken |
| `kern/04-kontext.md` | der Kontext-Haushalt: Mitschrieb, Handoff-Zyklus, Budget-Sensor |
| `kern/rollen.md` | die drei Rollen, der kollisionsfreie Schnitt, die Modell-Wahl |
| `kern/task-format.md` | Geruest einer Aufgabe: Rolle, Files, Akzeptanz, Abhaengigkeit |
| `kern/rueckgabe-schema.md` | die vier Felder, mit denen ein Arbeiter meldet |
| `kern/antwortform.md` | die Antwortform an den Nutzer (im Flow, max. 5 Zeilen, Negativliste); wird `.claude/output-styles/scratchpad-projektleiter.md` |
| `agent/commands/` | `/brainstorm` `/plan` `/build` `/loop` `/handoff` `/resume` |
| `agent/skills/grill-me/` | springt bei einer neu beschriebenen Idee von selbst an |
| `agent/settings-hooks.json` | verdrahtet die vier Waechter, wird in die `settings.json` gemerged |
| `agent/AGENTS-block.md` | derselbe Inhalt fuer Werkzeuge ohne Kurzbefehle |
| `hooks/` | die vier Waechter, `hook_util.py`, dazu die Selbsttests (nicht mitinstalliert) |
| `vorlagen/` | `.claude/tasks/README.md` fuers Projekt und ein ausgefuellter Beispielplan |
| `treiber.py` + `test_treiber.py` | der unbeaufsichtigte Handoff-Zyklus von aussen (bleibt im Klon, wird nicht mitinstalliert; Aufruf mit `--projekt`) |
| `install_settings.py` | merged Waechter und Output-Style in eine vorhandene `settings.json`, ohne fremde Eintraege zu verlieren (wird vom Installer aufgerufen, bleibt im Klon) |
| `KONZEPT.md` | warum das alles so geschnitten ist — die Begruendungen |

Die Kurzbefehle enthalten selbst keinen Inhalt, sondern verweisen auf die passende Datei
in `vorgehen/`. So gibt es genau **eine** Stelle, an der etwas steht, auch wenn dieselbe
Anleitung ueber drei Wege erreichbar ist (Befehl, Selbststarter, `AGENTS.md`).

**Was bewusst fehlt:** Rollen-Kurzbefehle (die Playbooks stehen in `rollen.md` und
wandern als Text in den Auftrag), Git-Blocker, Antwortform-Zwang per Hook, jede
Stack-Bindung. Begruendung je in `KONZEPT.md`.

---

## Was das Werkzeug koennen muss

Zwei Faehigkeiten, und beide sind optional:

**Mehrere Arbeiter gleichzeitig starten?** Dann baut ein Gespraech als Bauleiter und
verteilt an frische Arbeiter (**Modus A**). Sonst arbeitet dasselbe Gespraech den Plan
der Reihe nach ab (**Modus B**) — laenger, und der Kontext laeuft voll.

**Programme bei Ereignissen ausfuehren (Hooks)?** Dann laufen die vier Waechter mit.
Sonst gelten dieselben Regeln, aber niemand haelt dich auf.

Claude Code kann beides. Mischfaelle brauchen niemanden zu kuemmern: kennt ein Werkzeug
die Kurzbefehle, kann aber keine Arbeiter starten, faellt es von selbst auf den
sequenziellen Weg zurueck und sagt das zu Beginn in einem Satz.

---

## Drei Merksaetze zum Mitnehmen

> **Das Harness misst, das Modell urteilt, der Nutzer entscheidet.**
> Genau in dieser Reihenfolge. Deshalb gibt es genau einen selbsttaetigen Sensor — den,
> dessen Groesse sich als Zahl messen laesst.

> **Dispatch fuer Erzeugen, Loop fuer Konvergieren.**
> Einmalige, disjunkte Aufgaben werden verteilt. Wiederholt wird nur gegen ein
> Kriterium, das ausserhalb des Modells liegt.

> **Ein voller Kontext ist nicht nur teurer, er ist auch duemmer.**
> Kosten sind Fenstergroesse **mal** Zuege, und im Ballast geht das Wesentliche unter.
> Trennen, verdichten, uebergeben — in dieser Reihenfolge.
