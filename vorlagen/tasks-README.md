# <AGENTENORDNER>/tasks/ — hier liegen die Pläne

Ein Plan pro Vorhaben, als `<AGENTENORDNER>/tasks/<slug>.md` (z.B.
`<AGENTENORDNER>/tasks/merkliste.md`). Fertige Pläne werden **nie gelöscht**, sondern
nach `<AGENTENORDNER>/tasks/done/` verschoben, sie sind die Geschichte des Projekts.

Der Plan ist die gemeinsame Wahrheit zwischen dir und dem Bau-Schritt. Was nicht im Plan
steht, wird nicht gebaut; was gebaut wurde, wird im Plan abgehakt.

## Die Status-Zeile ist ein Vertrag

Im Kopf jedes Plans steht genau eine dieser drei Zeilen, exakt so geschrieben:

- `Status: entwurf`: die Plan-Phase hat den Plan angelegt, der User hat ihn noch nicht
  freigegeben.
- `Status: im-bau`: die Bau-Phase hat begonnen.
- `Status: fertig`: alle Tasks sind abgehakt oder begründet gestrichen.

Ein Wächter liest diese Zeile. Andere Wörter, andere Schreibweise oder eine fehlende
Zeile brechen ihn.

## Fertig heisst was (steht einmal im Plan-Kopf, gilt für jeden Task)

- Alle Akzeptanzkriterien des Tasks laufen als Tests grün.
- Bei Logik: der Rot-Beleg lag vor (der Test war erst rot, dann grün).
- Keine Datei ausserhalb der Files-Liste des Tasks wurde angefasst.
- Der Task ist im Plan abgehakt.
- Ein Commit für diesen Schritt existiert.

## Das Task-Gerüst

```markdown
#### Task N — <kurzer Titel>
- [ ] offen
- **Rolle:** backend | frontend | fullstack
- **Files:** exakte Pfade, je mit (neu) oder (ändern)
- **Wiederverwendung:** bestehende Bausteine, die genutzt werden
- **Akzeptanz:** 1–3 Kriterien „Wenn <Auslöser>, dann <Ergebnis>", jedes wird ein Test
- **Test:** Testdatei + Kern-Assertion (der Test, der diesen Task rot→grün macht)
- **Abhängig von:** Task-Nummern oder „—"
```

Ein Task ist 2–5 Minuten Arbeit. Checkbox-Zustände sind `- [ ] offen` und
`- [x] erledigt`, sonst nichts.

Drei Regeln halten den Plan ehrlich, und alle drei sind der Grund, warum der Plan die
gemeinsame Wahrheit bleibt:

- **Jeder offene Task trägt 1–3 testbare Kriterien** im Muster „Wenn <Auslöser>, dann
  <Ergebnis>" — eines pro Verhalten, jedes wird ein Test. Ohne sie ist nicht
  entscheidbar, ob der Task fertig ist, und „fertig" wird zur Meinung.
- **Umgesetzt heisst abgehakt**, sofort nach der Prüfung, Task für Task — nicht erst am
  Ende, sonst zeigt der Plan einen Stand, den es nie gab.
- **Verworfen heisst begründet durchgestrichen und dem User gesagt**, nie kommentarlos
  gelöscht. Eine still verschwundene Zeile ist der einzige Fall, bei dem sich der
  Plan-Wächter meldet.

Die verbindliche Fassung dieses Formats steht in
`<AGENTENORDNER>/vorgehen/task-format.md`; diese Datei hier ist die Kurzform zum
Nachschlagen. Ein ausgefüllter Beispielplan liegt daneben und zeigt, wie die Wellen
entstehen.
