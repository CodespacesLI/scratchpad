# Referenzen zur Uebung

Diese Liste ist fertig. Niemand sucht selbst Repositories, Tutorials oder Beispiele.
Kommst du beim Planen oder Bauen an ein Problem, das hier steht, holst du genau diesen
Eintrag: `/ref <slug>` in Claude, `Referenzen: <slug>` in Codex. Die Dateien landen per
Git in `<AGENTENORDNER>/references/sources/<slug>/`. Danach wird kopiert und
zugeschnitten. Neu geschrieben wird nur, wofuer es keine Vorlage gibt.

| Problem | Slug |
|---|---|
| Karten mit Maus und Tastatur zwischen Spalten verschieben | `dnd-kit` |
| Dialog, Auswahlfeld, Eingabefelder | `shadcn` |
| Daten im Browser speichern, kaputte Daten abfangen | `zustand` |
| Unit-Tests einrichten | `vitest` |
| Tests, die Elemente ueber Rolle und Namen finden | `testing-library` |
| Automatische Browser-Tests | `playwright` |

Der Ablauf steht in `<AGENTENORDNER>/vorgehen/referenzen-holen.md`. Repositories,
Branches, Lizenzen und Pfade wurden am **15.09.2026** per Git geprueft.

**Zielstack der Uebung:** Vite, React, TypeScript, Tailwind, Vitest, Playwright.

Jeder Eintrag hat einen `ref`-Block. Den liest der Agent maschinell: `pfade` ist die
Liste fuer `git sparse-checkout set --no-cone`, ein Pfad pro Zeile, `/` am Ende heisst
Ordner.

---

## dnd-kit: Board, Maus- und Tastatur-Verschieben

```ref
slug:   dnd-kit
repo:   https://github.com/clauderic/dnd-kit.git
ref:    master
lizenz: MIT
pfade:
  stories/2 - Presets/Sortable/MultipleContainers.tsx
  stories/2 - Presets/Sortable/multipleContainersKeyboardCoordinates.ts
  stories/components/Container/
  stories/components/Item/
  packages/core/src/components/Accessibility/defaults.ts
  LICENSE
```

| Datei | Vorlage fuer | Anpassen |
|---|---|---|
| `MultipleContainers.tsx` | Board mit Spalten und Karten, Maus- und Tastatur-Sensor, Ablage-Logik in `onDragOver` und `onDragEnd` | Container sind die drei Spalten, Items die Karten. Karte beim Ablegen **ans Ende** der Zielspalte haengen, keine Sortierung innerhalb einer Spalte. Trash, `createRange` und Story-Props entfernen. |
| `multipleContainersKeyboardCoordinates.ts` | Pfeiltasten wechseln die Zielspalte | Unveraendert kopieren. |
| `Container/`, `Item/` | Spalte und Karte inklusive Drag-Handle | CSS-Module durch Tailwind-Klassen ersetzen oder uebernehmen. `classnames` installieren oder durch `cn` ersetzen. |
| `Accessibility/defaults.ts` | Anleitung und Live-Meldungen fuer den Screenreader | Texte ins Deutsche uebersetzen, Karten- und Spaltentitel statt IDs nennen und als `accessibility={{ announcements, screenReaderInstructions }}` an `DndContext` geben. |

**Pakete:** `@dnd-kit/core@6.3.1 @dnd-kit/sortable@10.0.0 @dnd-kit/utilities@3.2.2`

**Achtung:** Der Branch `master` ist die stabile Linie 6.3.1. Auf `main` liegt die neue
Hauptversion `@dnd-kit/react` mit anderen Namen. Wer Code von `main` liest und
`@dnd-kit/core` installiert, bekommt nicht passende Imports. Deshalb steht hier `master`.

Die Tastaturbedienung ist eingebaut und entspricht Abnahmekriterium 5: Leertaste nimmt auf,
Pfeiltasten bewegen, Leertaste legt ab, Escape bricht ab.

## shadcn/ui: Dialog, Auswahlfeld, Formularfelder

```ref
slug:   shadcn
repo:   https://github.com/shadcn-ui/ui.git
ref:    main
lizenz: MIT
pfade:
  apps/v4/registry/new-york-v4/ui/dialog.tsx
  apps/v4/registry/new-york-v4/ui/select.tsx
  apps/v4/registry/new-york-v4/ui/button.tsx
  apps/v4/registry/new-york-v4/ui/input.tsx
  apps/v4/registry/new-york-v4/ui/textarea.tsx
  apps/v4/registry/new-york-v4/ui/label.tsx
  LICENSE.md
```

| Datei | Vorlage fuer | Anpassen |
|---|---|---|
| `dialog.tsx` | Karten-Dialog mit Fokusfalle, Fokus-Rueckgabe, `DialogTitle` als zugaenglichem Namen | Schliessen abfangen, wenn ungespeicherte Aenderungen vorliegen (`onOpenChange` und `onEscapeKeyDown`). |
| `select.tsx` | Prioritaet im Dialog und Prioritaetsfilter | Keine Anpassung. |
| `button.tsx`, `input.tsx`, `textarea.tsx`, `label.tsx` | Formularfelder im Dialog und Titelfilter | Keine Anpassung. |

**So wird kopiert:** `npx shadcn@latest init` und danach
`npx shadcn@latest add dialog select button input textarea label`. Die CLI kopiert genau
diese Dateien nach `src/components/ui/` und legt `src/lib/utils.ts` mit `cn` an. Die
lokalen Dateien zeigen vorab, welcher Code ins Projekt kommt. Wer von Hand kopiert, ersetzt
`from "cn"` durch `from "@/lib/utils"` und `@/registry/new-york-v4/ui/` durch
`@/components/ui/`.

## Zustand: Store mit lokaler Persistenz

```ref
slug:   zustand
repo:   https://github.com/pmndrs/zustand.git
ref:    main
lizenz: MIT
pfade:
  docs/reference/middlewares/persist.md
  docs/reference/integrations/persisting-store-data.md
  src/middleware/persist.ts
  tests/persistSync.test.tsx
  LICENSE
```

| Datei | Vorlage fuer | Anpassen |
|---|---|---|
| `docs/reference/middlewares/persist.md` | Store mit `persist`, `name`, `version`, `migrate`, `partialize` | Beispiel-Store kopieren und auf Karten und Spalten umbauen. |
| `persisting-store-data.md` | `onRehydrateStorage`, Reaktion auf Ladefehler | Bei Fehler leeren Zustand setzen und Meldungstext hinterlegen (Abnahmekriterium 9). |
| `src/middleware/persist.ts` | Nur lesen: `JSON.parse` in `createJSONStorage` und der `catch` in der Rehydrierung zeigen, wo kaputte Daten landen | Nichts kopieren, die Middleware wird als Paket genutzt. |
| `tests/persistSync.test.tsx` | Unit-Tests fuer Speichern, Laden und fehlerhaften Speicherinhalt | Testaufbau mit Mock-Storage uebernehmen, Store austauschen. |

**Paket:** `zustand`

**Zwei Fenster:** `persist` synchronisiert Browser-Tabs nicht von selbst.

## Vitest: Unit-Tests in der Vite-Konfiguration

```ref
slug:   vitest
repo:   https://github.com/vitest-dev/vitest.git
ref:    main
lizenz: MIT
pfade:
  examples/basic/
  LICENSE
```

| Datei | Vorlage fuer | Anpassen |
|---|---|---|
| `examples/basic/vite.config.ts` | `test`-Block direkt in der Vite-Config, keine zweite Build-Kette | `environment: 'jsdom'` setzen, damit `localStorage` im Test existiert. |
| `examples/basic/test/basic.test.ts` | Aufbau einer Testdatei | Auf Store und Datenmodell umschreiben. |
| `examples/basic/package.json` | Test-Script | Scripts uebernehmen. |

**Pakete:** `vitest jsdom`

## Testing Library: Abfragen nach Rolle und Namen

```ref
slug:   testing-library
repo:   https://github.com/testing-library/testing-library-docs.git
ref:    main
lizenz: MIT
pfade:
  docs/queries/about.mdx
  docs/queries/byrole.mdx
  docs/react-testing-library/example-intro.mdx
  docs/user-event/intro.mdx
  LICENSE
```

| Datei | Vorlage fuer | Anpassen |
|---|---|---|
| `example-intro.mdx` | Komplette React-Komponententest-Datei mit `render`, `screen`, `userEvent` | Auf Dialog und Filter umschreiben. |
| `byrole.mdx` | `getByRole('dialog', { name })`, `getByRole('button', { name })` | Deutsche zugaengliche Namen einsetzen. |
| `about.mdx` | Reihenfolge der Abfragen: Rolle vor Label vor Text vor Test-ID | Nur lesen. |
| `user-event/intro.mdx` | Tippen und Tastatur im Test | `userEvent.setup()` in jeder Testdatei. |

**Pakete:** `@testing-library/react @testing-library/user-event @testing-library/jest-dom`

## Playwright: Browser-Tests und Quality Gate

```ref
slug:   playwright
repo:   https://github.com/microsoft/playwright.git
ref:    main
lizenz: Apache-2.0
pfade:
  examples/todomvc/playwright.config.ts
  examples/todomvc/specs/
  examples/todomvc/tests/fixtures.ts
  examples/todomvc/tests/adding-todos/
  examples/todomvc/tests/editing-todos/
  examples/todomvc/tests/filtering-todos/
  LICENSE
```

| Datei | Vorlage fuer | Anpassen |
|---|---|---|
| `playwright.config.ts` | Konfiguration mit `webServer` und `baseURL` | Befehl auf `npm run dev` und den Vite-Port setzen. |
| `tests/fixtures.ts` | Gemeinsamer Startzustand pro Test | Leeren `localStorage` statt Todo-Seite vorbereiten. |
| `tests/adding-todos/` | Karte anlegen, leere Eingabe ablehnen | Todo durch Karte ersetzen. |
| `tests/editing-todos/` | Bearbeiten, Escape bricht ab, Speichern | Auf den Karten-Dialog umschreiben. |
| `tests/filtering-todos/` | Filter pruefen, ohne feste Wartezeiten | Auf Prioritaets- und Textfilter umschreiben. |
| `specs/` | Testplan als Markdown neben den Specs | Qualitaetskriterien aus dem Arbeitsblatt eintragen. |

**Paket:** `@playwright/test`
