# Referenzen holen: fertigen Code lokal bereitlegen

**Eingang:** `<AGENTENORDNER>/references/referenzen.md`, die feste Quellenliste. Sie nennt
pro Quelle Repository, Branch, Lizenz, die genauen Pfade und wofuer jede Datei die
Vorlage ist. Niemand sucht selbst.

**Ausgang:** die Dateien der angefragten Eintraege liegen unter
`<AGENTENORDNER>/references/sources/<slug>/`, und `<AGENTENORDNER>/references/INDEX.md`
sagt pro Datei: Commit, Lizenz, lokaler Pfad, Vorlage fuer was.

**Wozu der Index:** `/ref` laedt fertigen Code herunter und schreibt pro Datei den lokalen
Pfad und eine Erklaerung, wofuer sie die Vorlage ist, in `INDEX.md`. Der Plan-Schritt liest
`INDEX.md` gleich zu Beginn und weiss so bei jedem Problem sofort, wo passender Code liegt.
Im echten Leben liest der Agent die geholten Dateien selbst und schreibt die Erklaerung
selbst. In dieser Uebung gibt `referenzen.md` beides vor: welche Dateien geholt werden und
die Erklaerung dazu. So werden keine ganzen Repositories geladen, und der Index ist bei
allen gleich.

**Wann:** Nach dem Brainstorm, vor dem Plan. Welche Vorlagen genutzt werden, entscheidet
der User schon beim Klaeren der Anforderungen; der Brief nennt die gewaehlten Slugs je mit
dem Problem, das sie loesen. Geholt werden genau diese Slugs, nicht alles auf Vorrat. Der
Plan liest danach `INDEX.md`, der Bau kopiert nur noch, was im Task-Feld „Vorlage:“ steht.

**Warum:** Gepflegter, getesteter Code aus einem echten Repository ist die schnellste und
sicherste Vorlage. Aus dem Gedaechtnis geschriebener Code trifft oft eine alte API oder
vergisst Randfaelle wie Tastatur und Screenreader. Eine Websuche liefert Tutorials fuer
eine andere Version. Lokal geklonte Dateien haben einen festen Commit, und der Agent liest
genau das, was er kopiert.

Dieser Schritt holt und ordnet nur. Er baut keinen Anwendungscode.

## Ablauf

1. **Git pruefen:** `git --version`. Fehlt Git, abbrechen und das melden.
2. **Liste lesen.** Das Argument nennt die Slugs der Eintraege, die geholt werden. `all`
   holt alle. Ist das Argument leer, nennst du dem User jeden Slug mit seinem Thema in
   einer Zeile, fragst, welche er braucht, und stoppst.
3. **Klone aus dem Projekt-Commit halten.** Steht in der `.gitignore` im Projektwurzel
   die Zeile `<AGENTENORDNER>/references/sources/` noch nicht, haengst du sie an. Die
   Klone sind fremde Repositories und gehoeren nicht in die Historie des Projekts.
4. **Pro Eintrag holen.** Das Ziel ist `Z = <AGENTENORDNER>/references/sources/<slug>`.

   Ist `Z` noch nicht vorhanden:

   ```text
   git clone --depth 1 --filter=blob:none --sparse --branch <ref> <repo> "Z"
   git -C "Z" sparse-checkout set --no-cone "<pfad 1>" "<pfad 2>" ...
   ```

   Ist `Z` schon vorhanden, wird aktualisiert:

   ```text
   git -C "Z" fetch --depth 1 --filter=blob:none origin <ref>
   git -C "Z" reset --hard FETCH_HEAD
   git -C "Z" sparse-checkout set --no-cone "<pfad 1>" "<pfad 2>" ...
   ```

   - `--depth 1 --filter=blob:none` und `sparse-checkout` laden nur die gelisteten
     Dateien. Ein volles Playwright-Repository waere mehrere hundert Megabyte gross.
   - Jeder Pfad steht in Anfuehrungszeichen, weil einige Leerzeichen enthalten. Pfade
     beginnen **nie** mit `/`, weil Git Bash unter Windows sie sonst in Windows-Pfade
     umschreibt. Die Git-Warnung „pass a leading slash before paths“ ist deshalb
     erwartet und harmlos.
   - `reset --hard` ist nur innerhalb von `references/sources/` erlaubt, weil dort keine
     eigene Arbeit liegt. Im Projekt selbst gilt weiter: nichts zurueckdrehen.
5. **Pruefen statt glauben.** Nach dem Holen muss jeder gelistete Pfad lokal existieren.
   Fehlt einer, markierst du ihn im Index als `FEHLT`. Du suchst keinen Ersatz und raetst
   keinen neuen Pfad. Den Commit liest du mit `git -C "Z" rev-parse --short HEAD`.
6. **`<AGENTENORDNER>/references/INDEX.md` fortschreiben.** Gibt es die Datei schon,
   ersetzt du nur die Abschnitte der gerade geholten Slugs. Alle anderen Abschnitte
   bleiben stehen. Pro Quelle gibt es eine Kopfzeile mit Slug, Repository, Commit und
   Lizenz. Darunter steht eine Tabelle `lokale Datei | Vorlage fuer | Anpassen`. Die
   Spalten „Vorlage fuer“ und „Anpassen“ uebernimmst du aus `referenzen.md`, ohne eigene
   Deutung.
7. **Melden und stoppen.** Nenne die geholten Slugs, jeden fehlenden Pfad mit dem Wort
   `FEHLT` davor und den Pfad zu `INDEX.md`. Fehlt nichts, steht `FEHLT` nicht in der
   Meldung.

## Fehlerfaelle

Ist ein Repository nicht erreichbar oder fehlt ein Branch, meldest du genau diesen
Eintrag als Fehler und holst die uebrigen weiter. Fuer einen gescheiterten Eintrag steht
im Index `FEHLT`, keine erfundene Beschreibung.

## Regeln fuer das Kopieren (Plan und Bau)

- **Plan:** Zu Beginn liest du `INDEX.md`. Jeder Task, zu dem dort geholter Code passt,
  traegt das Feld **Vorlage:** mit dem lokalen Pfad
  (`<AGENTENORDNER>/vorgehen/task-format.md`). Grundlage ist nur, was in `INDEX.md` steht.
- **Bau:** Hat ein Task eine Vorlage, kopierst du zuerst die Datei ins Projekt und
  schneidest sie dann auf die Aufgabe zu: Namen, deutsche Texte, ueberfluessige Teile
  raus. Du schreibst nichts neu, wofuer eine Vorlage bereitliegt. Grundlage ist nur das
  Feld „Vorlage:“ des Tasks. Welche Vorlagen es gibt, ist mit dem Brief entschieden.
- **Herkunft:** Die erste Kommentarzeile jeder kopierten Datei lautet
  `Vorlage: <repo>@<commit> <pfad> (<Lizenz>)`. Das genuegt MIT und Apache-2.0 fuer eine
  Uebung und macht spaeter nachvollziehbar, woher der Code kommt.
- **Nur gelistete Quellen.** Keine freie Websuche, keine Quelle ausserhalb der Liste.
- **`references/sources/` bleibt unveraendert.** Kopiert wird ins Projekt, nie zurueck.
- **Test zuerst gilt auch hier.** Kopierter Code ist in diesem Projekt noch ungetestet.
  Der Test des Tasks wird zuerst rot und dann mit der angepassten Kopie gruen.
