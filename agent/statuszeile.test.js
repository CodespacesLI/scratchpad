// Selbsttest fuer statuszeile.js — Aufruf: `node --test agent/statuszeile.test.js`.
// Nur Node-Bordmittel (node:test), laeuft gleich unter Windows, macOS und Linux.
"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");

const SKRIPT = path.join(__dirname, "statuszeile.js");
const {
  kontextTokens,
  fensterGroesse,
  formatTokens,
  gitBranch,
  baueZeile,
} = require(SKRIPT);

const ANSI = /\x1b\[[0-9;]*m/g;
const ohneFarbe = (text) => text.replace(ANSI, "");

function transcript(zeilen) {
  const ordner = fs.mkdtempSync(path.join(os.tmpdir(), "statuszeile-"));
  const pfad = path.join(ordner, "transcript.jsonl");
  fs.writeFileSync(pfad, zeilen.join("\n") + "\n", "utf8");
  return pfad;
}

const nutzung = (usage) => JSON.stringify({ type: "assistant", message: { usage } });

test.describe("kontextTokens", () => {
  test("nimmt den letzten Usage-Eintrag und summiert alle vier Felder", () => {
    const pfad = transcript([
      nutzung({ input_tokens: 999, output_tokens: 999 }),
      JSON.stringify({ type: "user", message: { content: "hallo" } }),
      nutzung({
        input_tokens: 10,
        cache_read_input_tokens: 40000,
        cache_creation_input_tokens: 2000,
        output_tokens: 500,
      }),
      JSON.stringify({ type: "user", message: { content: "ohne usage" } }),
    ]);
    assert.equal(kontextTokens(pfad), 42510);
  });

  test("ueberspringt kaputte Zeilen", () => {
    const pfad = transcript([nutzung({ input_tokens: 7 }), "{kein json"]);
    assert.equal(kontextTokens(pfad), 7);
  });

  test("fehlender Pfad, fehlende Datei oder keine Usage ergibt null", () => {
    assert.equal(kontextTokens(undefined), null);
    assert.equal(kontextTokens(path.join(os.tmpdir(), "gibt-es-nicht.jsonl")), null);
    assert.equal(kontextTokens(transcript([JSON.stringify({ type: "user" })])), null);
  });
});

test.describe("fensterGroesse", () => {
  test("nimmt die Fenstergroesse aus den Sitzungsdaten, wenn vorhanden", () => {
    assert.equal(fensterGroesse({ context_window: { context_window_size: 400000 } }), 400000);
  });

  test("erkennt das 1M-Fenster an der Modell-Id", () => {
    assert.equal(fensterGroesse({ model: { id: "claude-opus-5[1m]" } }), 1000000);
  });

  test("faellt sonst auf 200k zurueck", () => {
    assert.equal(fensterGroesse({ model: { id: "claude-sonnet-4-5" } }), 200000);
    assert.equal(fensterGroesse({}), 200000);
  });
});

test.describe("formatTokens", () => {
  test("kurze Schreibweise fuer Tausender und Millionen", () => {
    assert.equal(formatTokens(512), "512");
    assert.equal(formatTokens(42510), "42.5k");
    assert.equal(formatTokens(200000), "200k");
    assert.equal(formatTokens(1000000), "1M");
  });
});

test.describe("gitBranch", () => {
  const git = (args, cwd) => spawnSync("git", args, { cwd, encoding: "utf8" });
  const ohneGit = git(["--version"]).status !== 0;

  test("frisches Git-Projekt ohne Commit zeigt schon den Branch", { skip: ohneGit }, () => {
    const ordner = fs.mkdtempSync(path.join(os.tmpdir(), "statuszeile-git-"));
    git(["init", "-q"], ordner);
    git(["symbolic-ref", "HEAD", "refs/heads/uebung"], ordner);
    assert.equal(gitBranch(ordner), "uebung");
  });

  test("kein Git-Projekt ergibt null", () => {
    const ordner = fs.mkdtempSync(path.join(os.tmpdir(), "statuszeile-ohne-git-"));
    assert.equal(gitBranch(path.join(ordner, "gibt-es-nicht")), null);
  });
});

test.describe("baueZeile", () => {
  test("zeigt Modell, Branch, Kontext mit Prozent und Kosten", () => {
    const pfad = transcript([nutzung({ input_tokens: 50000 })]);
    const zeile = ohneFarbe(
      baueZeile(
        {
          model: { id: "claude-sonnet-4-5", display_name: "Sonnet 4.5" },
          transcript_path: pfad,
          cost: { total_cost_usd: 0.12346 },
        },
        () => "main"
      )
    );
    assert.equal(zeile, "Sonnet 4.5 | git: main | Kontext 50k/200k (25%) | $0.1235");
  });

  test("fehlende Felder: kein Absturz, Platzhalter statt Luecke", () => {
    const zeile = ohneFarbe(baueZeile({}, () => null));
    assert.equal(zeile, "? | git: -");
  });

  test("hohe Auslastung bekommt eine gueltige Farbe (kein 'undefined')", () => {
    const pfad = transcript([nutzung({ input_tokens: 190000 })]);
    const zeile = baueZeile({ transcript_path: pfad }, () => "main");
    assert(!zeile.includes("undefined"), zeile);
    assert.match(ohneFarbe(zeile), /Kontext 190k\/200k \(95%\)/);
  });

  test("nur ASCII, damit alte Windows-Konsolen nichts verstuemmeln", () => {
    const pfad = transcript([nutzung({ input_tokens: 1234 })]);
    const zeile = ohneFarbe(
      baueZeile({ model: { display_name: "Opus" }, transcript_path: pfad, cost: { total_cost_usd: 1 } }, () => "feature/x")
    );
    assert.match(zeile, /^[\x20-\x7e]*$/);
  });
});

test("als Befehl: liest die Sitzung von stdin und schreibt eine Zeile", () => {
  const proc = spawnSync(process.execPath, [SKRIPT], {
    input: JSON.stringify({ model: { display_name: "Opus" }, cost: { total_cost_usd: 0 } }),
    encoding: "utf8",
  });
  assert.equal(proc.status, 0, proc.stderr);
  assert.match(ohneFarbe(proc.stdout), /^Opus \| git: .+ \| \$0\.0000$/);
});

test("als Befehl: kaputtes stdin bricht die Statuszeile nicht", () => {
  const proc = spawnSync(process.execPath, [SKRIPT], { input: "{kaputt", encoding: "utf8" });
  assert.equal(proc.status, 0, proc.stderr);
  assert.match(ohneFarbe(proc.stdout), /^\? \| git: /);
});
