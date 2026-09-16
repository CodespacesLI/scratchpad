# Task-Format — das Gerüst jedes Tasks im Plan

Pläne liegen im Projekt unter `<AGENTENORDNER>/tasks/<slug>.md`, fertige Pläne unter
`<AGENTENORDNER>/tasks/done/` — verschoben, nie gelöscht. Zone 3 eines Plans besteht
ausschliesslich aus Tasks in diesem Format.

## Der Plan-Kopf

Jeder Plan beginnt mit Titel, Status-Zeile und der „Fertig heisst was"-Liste:

```markdown
# Plan: <Feature-Name>

Status: entwurf

## Fertig heisst was (gilt für jeden Task)
- Alle Akzeptanzkriterien des Tasks laufen als Tests grün.
- Bei Logik: der Rot-Beleg lag vor (Test war erst rot, dann grün).
- Keine Datei ausserhalb der Files-Liste des Tasks wurde angefasst.
- Der Task ist im Plan abgehakt.
- Ein Commit für diesen Schritt existiert.
```

**Die Status-Zeile ist ein Vertrag.** Genau drei Werte, exakt so geschrieben:
`Status: entwurf` (die Plan-Phase legt den Plan so an) → `Status: im-bau` (die
Bau-Phase setzt das beim Start) → `Status: fertig` (die Bau-Phase setzt das, wenn alle
Tasks abgehakt oder begründet gestrichen sind). Ein Wächter liest diese Zeile; jede
Abweichung in Schreibweise oder Wortwahl bricht ihn.

## Das Task-Gerüst

```markdown
#### Task N — <kurzer Titel>
- [ ] offen
- **Rolle:** backend | frontend | fullstack
- **Files:** exakte Pfade, je mit (neu) oder (ändern)
- **Wiederverwendung:** bestehende Bausteine, die genutzt werden
- **Vorlage:** lokaler Pfad aus `<AGENTENORDNER>/references/INDEX.md`, der kopiert und angepasst wird, oder „—"
- **Akzeptanz:** 1–3 testbare EARS-Kriterien „Wenn <Auslöser>, dann <Ergebnis>", jedes wird ein Test
- **Test:** Testdatei + Kern-Assertion (der Test, der diesen Task rot→grün macht)
- **Abhängig von:** Task-Nummern oder „—"
```

## Regeln

- **Grösse:** ein Task ist 2–5 Minuten Arbeit. Wird er grösser, teile ihn.
- **Akzeptanz ist kein Wunsch, sondern ein Test.** Jeder offene Task trägt **1–3
  testbare Kriterien im EARS-Format**: „Wenn <Auslöser>, dann <Ergebnis>". „Wenn das
  Feld leer ist, dann erscheint die Meldung ‚Bitte ausfüllen'" lässt sich prüfen.
  „Formular validieren" nicht — es nennt weder Auslöser noch Ergebnis und lässt sich
  deshalb weder bauen noch widerlegen. Solche Sätze gehören in die EARS-Form
  umgeschrieben, bevor gebaut wird.
- **Vorlage vor Neubau.** Nennt der Task eine Vorlage, wird die Datei kopiert und
  zugeschnitten statt neu geschrieben (`<AGENTENORDNER>/vorgehen/referenzen-holen.md`,
  Abschnitt „Regeln fuer das Kopieren“).
- **Files ist eine Zusage.** Der Arbeiter ändert nur diese Dateien. Braucht er eine
  fremde, meldet er das unter OFFEN, statt sie anzufassen.
- **Checkbox-Zustände:** `- [ ] offen` und `- [x] erledigt`, nichts anderes.
- **Umgesetzte Tasks werden sofort nach der Verifikation abgehakt**, Task für Task,
  nie gesammelt am Schluss.
- **Verworfene Tasks werden begründet durchgestrichen, nie gelöscht**, und dem User
  gesagt. Ein stillschweigend verschwundener Task ist der häufigste Plan-Betrug.
- **Der fertige Plan wird nach `<AGENTENORDNER>/tasks/done/` verschoben, nie
  gelöscht.** Er ist die Spur, an der später nachvollziehbar bleibt, was warum
  gebaut wurde.
