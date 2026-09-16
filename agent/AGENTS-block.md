## scratchpad — vier Kern-Dateien, ein Vorgehen

Dieses Projekt arbeitet in drei Phasen plus einem Kontext-Haushalt, der quer durch alle
drei laeuft. Der ganze Inhalt liegt als reine Prosa in `<AGENTENORDNER>/vorgehen/`. Du
liest die passende Datei und folgst ihr woertlich.

| Der Nutzer sagt | Du liest und befolgst |
|---|---|
| `Brainstorm: ...` | `<AGENTENORDNER>/vorgehen/01-brainstorm.md` |
| `Referenzen: ...` / `Hole Referenzen` | `<AGENTENORDNER>/vorgehen/referenzen-holen.md` |
| `Plane: ...` | `<AGENTENORDNER>/vorgehen/02-plan.md` |
| `Baue: ...` / `Baue den Plan` | `<AGENTENORDNER>/vorgehen/03-build.md`, **Modus B** |
| „mein Kontext wird voll" / lange Sitzung | `<AGENTENORDNER>/vorgehen/04-kontext.md` |

Modus B heisst: du baust die Aufgaben des Plans **selbst und nacheinander**, eine nach
der anderen, statt sie an parallele Arbeiter zu verteilen. Nach jeder fertigen Aufgabe
haekst du sie in der Plandatei unter `<AGENTENORDNER>/tasks/` sofort ab (`- [ ]` wird zu
`- [x]`) und faengst erst dann die naechste an. Du baust **alle** offenen Aufgaben am Stueck,
ohne nach einem Teil anzuhalten oder auf ein Zwischen-Okay zu warten. Anhalten darfst du
nur bei einer echten Blockade, die der Plan nicht regelt und ohne Entscheidung des Nutzers
falsch gebaut wuerde, oder wenn dein Kontext voll ist (dann Handoff-Hinweis, siehe
`<AGENTENORDNER>/vorgehen/04-kontext.md`). Nennt der Nutzer ausdruecklich eine Teilmenge,
gilt diese. Wird `Baue:` nach einem Handoff erneut geschickt, machst du beim ersten offenen
Task weiter. Nachschlagewerke waehrend des Bauens:
`<AGENTENORDNER>/vorgehen/task-format.md` (Aufbau einer Aufgabe),
`<AGENTENORDNER>/vorgehen/rollen.md` (Schnitt und Modell-Wahl) und
`<AGENTENORDNER>/vorgehen/rueckgabe-schema.md` (wie du berichtest).

Feste Regeln, die ueber allem stehen:

- **Test zuerst.** Bei Fehlerbehebungen und bei Logik schreibst du zuerst den Test,
  laesst ihn einmal **rot** laufen, zeigst diese rote Ausgabe, und baust erst dann bis
  gruen. Ohne gesehenes Rot weisst du nicht, ob der Test den Fehler ueberhaupt trifft.
- **Antwortform.** Jede Antwort an den Nutzer folgt
  `<AGENTENORDNER>/vorgehen/antwortform.md` — verbindlich, denn in dieser Betriebsart
  gibt es keinen anderen Kanal, der dir die Form vorgibt. Kurz: der Nutzer ist
  Entwickler, du redest **im Flow** und setzt am Ausloeser an — wer was tut, was das
  System daraufhin macht, wo es kippt —, und du bleibst bei **hoechstens 5 Zeilen**. Eine
  Ja/Nein-Frage beantwortest du zuerst mit „Ja." oder „Nein.", danach hoechstens zwei
  Saetze Begruendung. Nicht in die Antwort gehoeren: Einleitungen,
  Schluss-Zusammenfassungen, Aufzaehlungen dessen, was du getan hast, Gedankenstriche,
  Emojis und naechste Schritte, um die niemand gebeten hat; bist du unsicher, fragst du
  nach, statt drei Varianten auszubreiten. **Technik, wenn sie gebraucht wird:** Pfade,
  Klassen-, Framework- und Waechter-Namen kommen in die Antwort, wenn der Nutzer danach
  fragt oder sie zum Handeln braucht — dann direkt, ohne Verpackung; die
  `Pfad:Zeile`-Belege aus Arbeiter-Rueckgaben bleiben intern. **Nie gekuerzt** werden
  Fehlschlaege, rote Tests, unverifizierte Zahlen, Sicherheits- und
  Datenverlustrisiken und echte Unsicherheit: der Deckel gilt fuer Bequemlichkeit, nicht
  fuer Wahrheit.
- **Eine Aufgabe nach der anderen, nie zwei parallel am selben Code.** Liegen mehrere
  Aufgaben vor dir und kannst du Arbeiter starten, delegierst du sie weiter, statt alle
  im eigenen Fenster zu erledigen: Aufgaben in einem Fenster addieren sich nicht, sie
  multiplizieren sich, weil jeder Zug den gesamten bisherigen Kontext erneut liest.
  Selbst erledigst du nur, was zusammen unter ~15 Minuten und unter fuenf Dateien
  bleibt. In Modus B gilt dasselbe sinngemaess: eine Aufgabe zu Ende bringen, abhaken,
  dann die naechste — nie zwei angefangene Umbauten nebeneinander am selben Code.
- **Jede Runde ist ein frischer Dispatch.** Keine Runde setzt die Arbeiter der Vorrunde
  fort, und gefixt wird ueber **einen** nacheinander gestarteten Fix-Arbeiter, nie ueber
  mehrere parallele Fixer auf demselben Code — zwei Fixer in derselben Datei
  ueberschreiben sich gegenseitig, und hinterher weiss niemand, welche Fassung gewonnen
  hat.
- **Arbeiter-Budget ~120k.** Kein Arbeiter bekommt ueber ~120k Tokens hinaus
  Folgearbeit: er schliesst am naechsten natuerlichen Uebergabepunkt ab, gibt einen
  kompakten Stand-Brief zurueck, und die Restarbeit geht an einen **frischen** Arbeiter.
  Ausnahme sind reine Test- oder Build-Auslaeufe, die duerfen auslaufen. In Modus B bist
  du selbst dieser Arbeiter — dann greift der Handoff-Zyklus aus
  `<AGENTENORDNER>/vorgehen/04-kontext.md`.
- **Schleife oder Arbeiter.** Denselben Auftrag wiederholst du nur, wenn es ein
  messbares Fertig-Kriterium gibt, jede Runde frisch startet und die Konvergenz
  ueberwacht wird — sonst wird die Arbeit in einmalige Aufgaben geschnitten.
  Kurz: **Dispatch fuer Erzeugen, Loop fuer Konvergieren.**
- **Der Plan wird nicht still gekuerzt.** Jeder offene Task traegt 1–3 testbare
  Kriterien im Muster „Wenn <Ausloeser>, dann <Ergebnis>". Ein umgesetzter Task wird
  abgehakt, ein verworfener **begruendet durchgestrichen** und dem Nutzer gesagt, nie
  kommentarlos geloescht. Fertige Plaene wandern nach `<AGENTENORDNER>/tasks/done/` und
  werden nie geloescht.
- **Kontext ist die knappe Ressource.** Gezielt lesen statt ganze Dateien, grosse
  Ausgaben filtern, und bei langen Laeufen den Stand mitschreiben
  (`<AGENTENORDNER>/state/`).
- **Nie pushen.** `git push` macht der Nutzer selbst.
- **Nichts zurueckdrehen.** Kein `git revert`, `git reset --hard`, `git checkout --`
  auf fremde Arbeit ohne ausdrueckliche Ansage.
- **Aenderungen am Vorgehen** gehoeren in den scratchpad-Klon, nie in diese kopierte
  Fassung, die naechste Installation ueberschreibt sie sonst.

### Was Modus A zusaetzlich hat

In einem Werkzeug mit Sub-Agenten und Hooks (heute Claude Code) kommen sieben Commands
und vier Waechter dazu:

| Command | Wofuer |
|---|---|
| `/brainstorm` | fragt die Idee auseinander, bevor geplant wird |
| `/ref` | holt die festen Referenz-Repositories per Git als Kopiervorlage |
| `/plan` | macht aus dem Brief einen freigabefertigen Plan, mit Gegenleser |
| `/build` | baut den Plan mit parallelen Arbeitern ab |
| `/loop` | schaerft den fertigen Unterschied nach, bis zwei saubere Runden in Folge |
| `/handoff` | schreibt den Stand nach `<AGENTENORDNER>/state/handoff-brief.md` |
| `/resume` | liest den Brief, prueft ihn gegen den Arbeitsbaum, macht weiter |

| Waechter | Was er tut |
|---|---|
| `guard_tdd` | beendet den Zug nicht, wenn Logik ohne begleitenden Test geaendert wurde |
| `guard_test_quality` | faengt Tests ab, die gar nicht rot werden koennen |
| `guard_plan_drift` | meldet eine Task-Zeile, die unbegruendet aus dem Plan verschwunden ist |
| `guard_context_budget` | misst den Kontextstand und warnt einmalig ab etwa 120 000 Tokens; mit `SCRATCHPAD_AUTO_HANDOFF=1` erzwingt er stattdessen den Handoff-Brief |

**Arbeiter startest du immer im Hintergrund, nie synchron.** Ein synchron gestarteter
Arbeiter haengt an deinem laufenden Zug: solange er laeuft, bist du nicht ansprechbar,
und ein Abbruch im Gespraech reisst seine Arbeit mit ab. Im Hintergrund laeuft er
unabhaengig weiter, das Gespraech bleibt frei, und seine Fertigstellung kommt als
Meldung zurueck.

Den Kontext-Zyklus loest kein Command und kein Waechter von selbst aus. Deinen eigenen
Fuellstand siehst du nicht, und der Nutzer muss ihn nicht ablesen: der Waechter misst ihn
nach jedem Zug und meldet sich bei etwa 120 000 Tokens. Meldet er sich, laesst du laufende
Arbeiter fertig werden, **schlaegst den Zyklus vor**, und der Nutzer tippt `/handoff`, dann `/clear`,
dann `/resume` und, wenn gerade gebaut wurde, wieder `/build`. Der Waechter darf einmal pro
Sitzung warnen und mit `SCRATCHPAD_AUTO_HANDOFF=1` jedes Zug-Ende blocken, bis der Brief
geschrieben ist, mehr nicht.

**Ehrlich dazugesagt, was dir in Modus B fehlt:** Diese Waechter laufen hier **nicht** —
niemand haelt dich auf, wenn du ohne Test baust, den Plan still kuerzt oder doch pushst;
die Regeln oben sind dann reine Selbstdisziplin. Und es gibt **keine parallelen
Arbeiter**: der Plan wird sequenziell abgearbeitet, das dauert laenger, dafuer
kollidiert nichts.
