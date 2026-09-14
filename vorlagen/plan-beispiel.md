# Plan: Merkliste

Status: entwurf

## Fertig heisst was (gilt für jeden Task)
- Alle Akzeptanzkriterien des Tasks laufen als Tests grün.
- Bei Logik: der Rot-Beleg lag vor (der Test war erst rot, dann grün).
- Keine Datei ausserhalb der Files-Liste des Tasks wurde angefasst.
- Der Task ist im Plan abgehakt.
- Ein Commit für diesen Schritt existiert.

## Zone 1 — Kurzfassung

Angemeldete Nutzer können einen Eintrag mit einem Klick merken und alle gemerkten
Einträge später auf einer eigenen Seite wiederfinden. Gemerkte Einträge gehören der
Person, die sie gemerkt hat, und niemandem sonst. Nicht dabei: Ordner, Notizen, Teilen.

## Zone 2 — Ablauf und Entscheidungen

1. Der Nutzer sieht bei jedem Eintrag ein Merken-Symbol.
2. Klick darauf merkt den Eintrag; ein zweiter Klick nimmt ihn wieder heraus.
3. Über das Menü erreicht er „Meine Merkliste" mit allen gemerkten Einträgen.
4. Ist die Liste leer, steht dort ein Hinweis statt einer leeren Fläche.

**Entscheidungen:** Merken ist ein Ein-Aus-Zustand, keine Mengenangabe. Die Liste ist
nach Merk-Zeitpunkt sortiert, neueste zuerst. Doppeltes Merken desselben Eintrags ist
kein Fehler, sondern wird still ignoriert.

**Offen für den User:** Sollen gemerkte Einträge verschwinden, wenn der Eintrag selbst
gelöscht wird, oder als „nicht mehr verfügbar" stehen bleiben? Empfehlung: verschwinden.

## Zone 3 — Tasks

### Welle 1 — Vertrag und Datenmodell (allein, nichts läuft parallel)

#### Task 1 — Schnittstelle und Tabelle festlegen
- [ ] offen
- **Rolle:** backend
- **Files:** `docs/schnittstellen/merkliste.md` (neu), `server/daten/merkliste-tabelle.sql` (neu)
- **Wiederverwendung:** Tabellen-Namensschema aus `server/daten/`, Antwortform der bestehenden Listen-Endpunkte
- **Akzeptanz:** Wenn die Migration läuft, dann existiert eine Tabelle `merkliste` mit Nutzer-Kennung, Eintrags-Kennung und Zeitpunkt, eindeutig je Paar. Wenn ein Entwickler die Vertragsdatei liest, dann findet er Pfad, Methode und eine vollständige Beispiel-Antwort für Liste, Merken und Entmerken.
- **Test:** `server/daten/merkliste-tabelle.test.sql`: zweimaliges Einfügen desselben Paars verletzt die Eindeutigkeit
- **Abhängig von:** —

### Welle 2 — Backend und Frontend parallel (disjunkte Files)

#### Task 2 — Merk-Logik im Dienst
- [ ] offen
- **Rolle:** backend
- **Files:** `server/dienste/merkliste-dienst.ts` (neu), `server/dienste/merkliste-dienst.test.ts` (neu)
- **Wiederverwendung:** `server/dienste/basis-dienst.ts` für Datenbank-Zugriff und Rechteprüfung
- **Akzeptanz:** Wenn ein Nutzer einen Eintrag merkt, den er schon gemerkt hat, dann bleibt es bei einem Eintrag und es entsteht kein Fehler. Wenn ein Nutzer die Merkliste abruft, dann enthält sie nur seine eigenen Einträge, neueste zuerst.
- **Test:** `server/dienste/merkliste-dienst.test.ts`: Abruf durch Nutzer B enthält keinen Eintrag von Nutzer A
- **Abhängig von:** 1

#### Task 3 — Merken-Knopf als Komponente
- [ ] offen
- **Rolle:** frontend
- **Files:** `web/komponenten/merken-knopf.tsx` (neu), `web/komponenten/merken-knopf.test.tsx` (neu)
- **Wiederverwendung:** `web/komponenten/symbol-knopf.tsx`, Beispiel-Antwort aus der Vertragsdatei als Platzhalter-Daten
- **Akzeptanz:** Wenn der Eintrag gemerkt ist, dann zeigt der Knopf den gefüllten Zustand und trägt den Namen „Merken aufheben". Wenn geklickt wird, während die Anfrage läuft, dann bleibt der Knopf gesperrt und löst nur einmal aus.
- **Test:** `web/komponenten/merken-knopf.test.tsx`: Doppelklick löst genau eine Aktion aus
- **Abhängig von:** 1

### Welle 3 — Backend und Frontend parallel (disjunkte Files)

#### Task 4 — Endpunkte bereitstellen
- [ ] offen
- **Rolle:** backend
- **Files:** `server/api/merkliste-endpunkt.ts` (neu), `server/api/merkliste-endpunkt.test.ts` (neu)
- **Wiederverwendung:** `server/dienste/merkliste-dienst.ts` aus Task 2, Fehlerformat der bestehenden Endpunkte
- **Akzeptanz:** Wenn ein nicht angemeldeter Aufruf kommt, dann antwortet der Endpunkt mit „nicht berechtigt" und ändert nichts. Wenn ein angemeldeter Nutzer merkt, dann entspricht die Antwort exakt der Beispiel-Antwort aus der Vertragsdatei.
- **Test:** `server/api/merkliste-endpunkt.test.ts`: Aufruf ohne Anmeldung wird abgewiesen
- **Abhängig von:** 2

#### Task 5 — Ansicht „Meine Merkliste"
- [ ] offen
- **Rolle:** frontend
- **Files:** `web/ansichten/merkliste-ansicht.tsx` (neu), `web/ansichten/merkliste-ansicht.test.tsx` (neu), `web/daten/merkliste-abfrage.ts` (neu)
- **Wiederverwendung:** `web/komponenten/liste.tsx`, `web/komponenten/leerzustand.tsx`
- **Akzeptanz:** Wenn die Merkliste leer ist, dann erscheint der Leerzustand mit Hinweistext statt einer leeren Fläche. Wenn die Abfrage fehlschlägt, dann erscheint eine Fehlermeldung mit Wiederholen-Knopf.
- **Test:** `web/ansichten/merkliste-ansicht.test.tsx`: leere Antwort zeigt den Leerzustand
- **Abhängig von:** 3

### Welle 4 — Integration (allein; alle gemeinsamen Dateien gehören hierher)

#### Task 6 — Verdrahten und durchgehender Pfad
- [ ] offen
- **Rolle:** fullstack
- **Files:** `server/api/registrierung.ts` (ändern), `web/routen.ts` (ändern), `texte/de.json` (ändern), `e2e/merkliste.spec.ts` (neu)
- **Wiederverwendung:** bestehende Routen- und Text-Registrierung
- **Akzeptanz:** Wenn ein Nutzer einen Eintrag merkt und dann die Merkliste öffnet, dann steht der Eintrag dort, ohne Neuladen der Seite. Wenn er ihn wieder entmerkt, dann verschwindet er aus der Liste.
- **Test:** `e2e/merkliste.spec.ts`: merken, öffnen, entmerken, Liste ist leer
- **Abhängig von:** 4, 5
