#!/usr/bin/env node
// Statuszeile fuer Claude Code: Modell | Git-Branch | Kontext-Verbrauch | Kosten.
//
// Claude Code ruft das Skript nach jeder Antwort auf und reicht die Sitzung als JSON
// auf stdin herein. Bewusst Node statt Python: Node ist fuer die Uebung ohnehin da und
// heisst auf Windows, macOS und Linux gleich (bei Python schwankt python/python3).
// Bewusst nur ASCII: Symbole fuer Branch oder Fuellstand werden in aelteren
// Windows-Konsolen zu Fragezeichen. Jeder Fehler endet still in einer kuerzeren Zeile, nie in einem Absturz.
"use strict";

const { execSync } = require("child_process");
const fs = require("fs");

const farbe = {
  aus: "\x1b[0m",
  blass: "\x1b[2m",
  cyan: "\x1b[36m",
  gruen: "\x1b[32m",
  gelb: "\x1b[33m",
  rot: "\x1b[31m",
  magenta: "\x1b[35m",
  grau: "\x1b[90m",
};

function formatTokens(n) {
  const kurz = (wert) => wert.toFixed(1).replace(/\.0$/, "");
  if (n >= 1000000) return kurz(n / 1000000) + "M";
  if (n >= 1000) return kurz(n / 1000) + "k";
  return String(n);
}

// Alles, was im Fenster liegt: frische Eingabe, Cache-Lesen, Cache-Schreiben, Ausgabe.
function summe(usage) {
  return (
    (usage.input_tokens || 0) +
    (usage.cache_read_input_tokens || 0) +
    (usage.cache_creation_input_tokens || 0) +
    (usage.output_tokens || 0)
  );
}

function hatUsage(usage) {
  return Boolean(usage) && (usage.input_tokens != null || usage.output_tokens != null);
}

// Kontext-Tokens = der letzte Usage-Eintrag im Transcript. Er zeigt, was beim letzten
// Aufruf tatsaechlich im Kontextfenster lag (nicht die Summe aller Aufrufe).
function kontextTokens(transcriptPfad) {
  try {
    if (!transcriptPfad || !fs.existsSync(transcriptPfad)) return null;
    const zeilen = fs.readFileSync(transcriptPfad, "utf8").split("\n");
    for (let i = zeilen.length - 1; i >= 0; i--) {
      const zeile = zeilen[i].trim();
      if (!zeile) continue;
      let eintrag;
      try {
        eintrag = JSON.parse(zeile);
      } catch {
        continue;
      }
      const usage = eintrag?.message?.usage;
      if (hatUsage(usage)) return summe(usage);
    }
  } catch {
    /* still: dann eben ohne Kontext-Anzeige */
  }
  return null;
}

// Neuere Claude-Code-Versionen liefern die Fenstergroesse mit; sonst verraet die
// Modell-Id das 1M-Fenster ("...[1m]"), alles andere hat 200k.
function fensterGroesse(daten) {
  const groesse = daten?.context_window?.context_window_size;
  if (typeof groesse === "number" && groesse > 0) return groesse;
  const modell = `${daten?.model?.id || ""} ${daten?.model?.display_name || ""}`;
  return /\[1m\]|\b1m\b/i.test(modell) ? 1000000 : 200000;
}

// `symbolic-ref` kennt den Branch schon vor dem ersten Commit (frisch angelegtes
// Uebungsprojekt); `rev-parse --abbrev-ref` scheitert dort. Ohne Branch (detached HEAD)
// zeigt die Zeile den kurzen Commit-Hash.
function gitBranch(ordner) {
  const git = (befehl) =>
    execSync(befehl, { cwd: ordner, stdio: ["ignore", "pipe", "ignore"], encoding: "utf8" }).trim();
  for (const befehl of ["git symbolic-ref --short -q HEAD", "git rev-parse --short HEAD"]) {
    try {
      const name = git(befehl);
      if (name) return name;
    } catch {
      /* naechster Versuch */
    }
  }
  return null;
}

function baueZeile(daten, branchVon = gitBranch) {
  const teile = [];

  const modell = daten?.model?.display_name || daten?.model?.id || "?";
  teile.push(`${farbe.cyan}${modell}${farbe.aus}`);

  const ordner = daten?.workspace?.current_dir || daten?.cwd || process.cwd();
  const branch = branchVon(ordner);
  teile.push(branch ? `${farbe.gruen}git: ${branch}${farbe.aus}` : `${farbe.grau}git: -${farbe.aus}`);

  let tokens = kontextTokens(daten?.transcript_path);
  const aktuell = daten?.context_window?.current_usage;
  if (tokens == null && hatUsage(aktuell)) tokens = summe(aktuell);
  if (tokens != null) {
    const fenster = fensterGroesse(daten);
    const prozent = Math.round((tokens / fenster) * 100);
    const ton = prozent >= 85 ? farbe.rot : prozent >= 60 ? farbe.gelb : farbe.gruen;
    teile.push(
      `${ton}Kontext ${formatTokens(tokens)}${farbe.blass}/${formatTokens(fenster)} (${prozent}%)${farbe.aus}`
    );
  }

  const kosten = daten?.cost?.total_cost_usd;
  if (typeof kosten === "number") {
    teile.push(`${farbe.magenta}$${kosten.toFixed(4)}${farbe.aus}`);
  }

  return teile.join(`${farbe.grau} | ${farbe.aus}`);
}

function main() {
  let daten = {};
  try {
    daten = JSON.parse(fs.readFileSync(0, "utf8") || "{}");
  } catch {
    daten = {};
  }
  process.stdout.write(baueZeile(daten));
}

module.exports = { formatTokens, kontextTokens, fensterGroesse, gitBranch, baueZeile };

if (require.main === module) main();
