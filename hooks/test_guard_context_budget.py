#!/usr/bin/env python3
"""Selbsttest fuer guard_context_budget.py — Aufruf: `python test_guard_context_budget.py`.

Reine asserts, kein Test-Framework (gleicher Runner wie die uebrigen Wächter-Tests).
Der Wächter misst den Kontextstand aus dem Transcript; die Tests legen dafür je ein
Wegwerf-Projekt mit einem handgeschriebenen Transcript im Temp-Verzeichnis an.

Abgedeckt: Schwelle (unter/über), ENV-Override inklusive kaputtem Wert, die einmalige
Warnung pro Sitzung (Stempel), der Auto-Modus (jeder Turn) samt Endlos-Block-Schutz
(Handoff-Brief im Turn geschrieben) und die fail-open-Pfade.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
HOOK = os.path.join(HOOKS_DIR, "guard_context_budget.py")

sys.path.insert(0, HOOKS_DIR)
import guard_context_budget  # noqa: E402  (erst nach dem sys.path-Eintrag importierbar)

# Aus dem Wächter gelesen, nicht abgeschrieben: der Installer ersetzt den
# Agenten-Ordner beim Kopieren, der Test muss trotzdem stimmen.
STEMPEL_REL = guard_context_budget.STEMPEL_DEFAULT
AGENT_DIR = guard_context_budget.DEFAULT_AGENT_DIR
HANDOFF_REL = AGENT_DIR + "/state/handoff-brief.md"


def usage_entry(total: int, sidechain: bool = False) -> dict:
    entry = {
        "type": "assistant",
        "message": {"usage": {
            "input_tokens": total,
            "cache_read_input_tokens": 0,
            "cache_creation_input_tokens": 0,
            "output_tokens": 0,
        }},
    }
    if sidechain:
        entry["isSidechain"] = True
    return entry


def human_prompt(text: str = "mach weiter") -> dict:
    return {"type": "user", "message": {"role": "user", "content": text}}


def write_entry(path: str) -> dict:
    return {
        "type": "assistant",
        "message": {"content": [
            {"type": "tool_use", "name": "Write", "input": {"file_path": path}},
        ]},
    }


def make_project(tmp: str, entries) -> tuple:
    """Wegwerf-Projekt mit Transcript; gibt (projekt_wurzel, transcript_pfad)."""
    root = os.path.join(tmp, "projekt")
    os.makedirs(root, exist_ok=True)
    transcript = os.path.join(tmp, "transcript.jsonl")
    with open(transcript, "w", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(json.dumps(entry) + "\n")
    return root, transcript


def run_hook(root: str, transcript=None, raw_stdin=None, env_extra=None, **payload_extra):
    payload = {"stop_hook_active": False, "session_id": "s1"}
    if transcript is not None:
        payload["transcript_path"] = transcript
    payload.update(payload_extra)
    data = raw_stdin if raw_stdin is not None else json.dumps(payload)
    env = dict(os.environ)
    env.pop(guard_context_budget.ENV_BUDGET, None)
    env.pop(guard_context_budget.ENV_AUTO, None)
    env["CLAUDE_PROJECT_DIR"] = root
    if env_extra:
        env.update(env_extra)
    return subprocess.run([sys.executable, HOOK], input=data, capture_output=True,
                          text=True, timeout=20, cwd=root, env=env)


def test_unter_schwelle_bleibt_still(tmp):
    root, tr = make_project(tmp, [human_prompt(), usage_entry(20_000)])
    proc = run_hook(root, tr)
    assert proc.returncode == 0, f"unter der Schwelle muss still sein: {proc.stderr}"
    assert proc.stderr.strip() == "", proc.stderr


def test_ueber_schwelle_warnt_einmal(tmp):
    root, tr = make_project(tmp, [human_prompt(), usage_entry(160_000)])
    proc = run_hook(root, tr)
    assert proc.returncode == 2, f"über der Schwelle muss warnen, war {proc.returncode}"
    assert "160k" in proc.stderr, proc.stderr
    assert "/handoff" in proc.stderr, proc.stderr
    assert "/clear" in proc.stderr and "/resume" in proc.stderr, proc.stderr
    assert os.path.isfile(os.path.join(root, STEMPEL_REL)), \
        f"Stempel gehört nach {STEMPEL_REL}"


def test_zweiter_turn_derselben_sitzung_still(tmp):
    root, tr = make_project(tmp, [human_prompt(), usage_entry(160_000)])
    assert run_hook(root, tr).returncode == 2, "erster Turn muss warnen"
    zweiter = run_hook(root, tr)
    assert zweiter.returncode == 0, "zweiter Turn derselben Sitzung darf nicht erneut nerven"


def test_neue_sitzung_warnt_wieder(tmp):
    root, tr = make_project(tmp, [human_prompt(), usage_entry(160_000)])
    assert run_hook(root, tr).returncode == 2
    proc = run_hook(root, tr, session_id="s2")
    assert proc.returncode == 2, "eine neue Sitzung bekommt die Warnung wieder"


def test_env_schwelle_greift(tmp):
    root, tr = make_project(tmp, [human_prompt(), usage_entry(25_000)])
    proc = run_hook(root, tr, env_extra={guard_context_budget.ENV_BUDGET: "20000"})
    assert proc.returncode == 2, "abgesenkte Schwelle muss greifen"
    assert "20k" in proc.stderr, proc.stderr


def test_kaputte_env_schwelle_faellt_auf_default(tmp):
    root, tr = make_project(tmp, [human_prompt(), usage_entry(100_000)])
    proc = run_hook(root, tr, env_extra={guard_context_budget.ENV_BUDGET: "viel"})
    assert proc.returncode == 0, "kaputter ENV-Wert muss auf den Default (150k) zurückfallen"


def test_summe_ueber_alle_usage_felder(tmp):
    entry = {"type": "assistant", "message": {"usage": {
        "input_tokens": 40_000, "cache_read_input_tokens": 60_000,
        "cache_creation_input_tokens": 30_000, "output_tokens": 30_000}}}
    root, tr = make_project(tmp, [human_prompt(), entry])
    proc = run_hook(root, tr)
    assert proc.returncode == 2, "160k Summe über alle Felder muss warnen"


def test_sidechain_zeile_zaehlt_nicht(tmp):
    """Die Subagenten-Zeile im Haupt-Transcript ist nicht der Kontext des Hauptthreads."""
    root, tr = make_project(tmp, [human_prompt(), usage_entry(20_000),
                                  usage_entry(900_000, sidechain=True)])
    proc = run_hook(root, tr)
    assert proc.returncode == 0, f"Sidechain darf nicht mitgemessen werden: {proc.stderr}"


def test_auto_modus_warnt_in_jedem_turn(tmp):
    root, tr = make_project(tmp, [human_prompt(), usage_entry(160_000)])
    env = {guard_context_budget.ENV_AUTO: "1"}
    erster = run_hook(root, tr, env_extra=env)
    assert erster.returncode == 2, "Auto-Modus muss blocken"
    assert "handoff-brief.md" in erster.stderr, erster.stderr
    zweiter = run_hook(root, tr, env_extra=env)
    assert zweiter.returncode == 2, "Auto-Modus wiederholt sich in JEDEM Turn"


def test_auto_modus_still_wenn_brief_im_turn_geschrieben(tmp):
    """Endlos-Block-Schutz: der Brief steht, der Turn darf enden."""
    root, tr = make_project(tmp, [human_prompt(),
                                  write_entry(HANDOFF_REL),
                                  usage_entry(160_000)])
    proc = run_hook(root, tr, env_extra={guard_context_budget.ENV_AUTO: "1"})
    assert proc.returncode == 0, f"geschriebener Brief muss den Block loesen: {proc.stderr}"


def test_auto_modus_ignoriert_brief_aus_altem_turn(tmp):
    """Ein Brief VOR dem letzten Prompt des Menschen gehört zu einem alten Turn."""
    root, tr = make_project(tmp, [human_prompt(), write_entry(HANDOFF_REL),
                                  human_prompt("und weiter"), usage_entry(160_000)])
    proc = run_hook(root, tr, env_extra={guard_context_budget.ENV_AUTO: "1"})
    assert proc.returncode == 2, "alter Brief darf den Block nicht loesen"


def test_auto_modus_nennt_treiber_weg_bei_marker(tmp):
    """Liegt der Treiber-Marker, nennt die Auflage den Treiber-Weg statt /clear + /resume:
    eine headless Sitzung kann die interaktiven Schritte nicht gehen — der Treiber
    startet die naechste Runde selbst, sobald der Turn endet."""
    root, tr = make_project(tmp, [human_prompt(), usage_entry(160_000)])
    marker = os.path.join(root, AGENT_DIR, "state", "treiber-aktiv")
    os.makedirs(os.path.dirname(marker), exist_ok=True)
    open(marker, "w").close()
    proc = run_hook(root, tr, env_extra={guard_context_budget.ENV_AUTO: "1"})
    assert proc.returncode == 2, "auch mit Marker muss der Auto-Modus blocken"
    assert "Treiber" in proc.stderr, proc.stderr
    assert "/clear" not in proc.stderr, \
        f"mit Treiber-Marker darf keine Handarbeit-Anweisung kommen: {proc.stderr}"


def test_loop_schutz_und_subagent_still(tmp):
    root, tr = make_project(tmp, [human_prompt(), usage_entry(160_000)])
    assert run_hook(root, tr, stop_hook_active=True).returncode == 0, "Loop-Schutz fehlt"
    assert run_hook(root, tr, agent_id="a1").returncode == 0, "Subagent-Stop muss still sein"


def test_fail_open_pfade(tmp):
    root, tr = make_project(tmp, [human_prompt(), usage_entry(160_000)])
    kaputt = run_hook(root, tr, raw_stdin="{kein json")
    assert kaputt.returncode == 0, "kaputtes stdin muss fail-open sein"
    assert "Traceback" not in kaputt.stderr, kaputt.stderr

    fehlt = run_hook(root, os.path.join(tmp, "gibt-es-nicht.jsonl"))
    assert fehlt.returncode == 0, "fehlendes Transcript muss fail-open sein"

    ohne = run_hook(root)
    assert ohne.returncode == 0, "fehlender transcript_path muss fail-open sein"

    muell = os.path.join(tmp, "muell.jsonl")
    with open(muell, "w", encoding="utf-8") as fh:
        fh.write("{kaputt\nnoch kaputter\n")
    assert run_hook(root, muell).returncode == 0, "unparsebares Transcript -> fail-open"

    ohne_usage = os.path.join(tmp, "ohne-usage.jsonl")
    with open(ohne_usage, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"type": "assistant", "message": {}}) + "\n")
    assert run_hook(root, ohne_usage).returncode == 0, "kein usage-Block -> fail-open"


def nennt_befehl(text: str, befehl: str) -> bool:
    """True, wenn `befehl` als eigenstaendiger Befehl im Text steht.

    Ohne diese Verengung zaehlte `/handoff-brief.md` als Nennung von `/handoff` —
    der Pfad im Text wuerde die fehlende Handlungsanweisung verdecken.
    """
    return re.search(re.escape(befehl) + r"(?![\w-])", text) is not None


def test_meldung_nennt_manuellen_weg_und_keinen_rollover(tmp):
    """Beide Zweige nennen den MANUELLEN Weg: /handoff, danach /clear, danach /resume.

    Das Schulungs-Harness startet nichts von selbst — kein Nachfolger, kein Rollover.
    Der Wächter sagt, was der Mensch jetzt tippt; auslösen tut er es nicht.
    """
    root, tr = make_project(tmp, [human_prompt(), usage_entry(160_000)])

    warn = run_hook(root, tr)
    assert warn.returncode == 2, f"über der Schwelle muss warnen: {warn.returncode}"
    for teil in ("/handoff", "/clear", "/resume"):
        assert nennt_befehl(warn.stderr, teil), f"{teil} fehlt im Warn-Zweig: {warn.stderr}"
    assert "rollover" not in warn.stderr.lower(), warn.stderr

    block = run_hook(root, tr, session_id="s2",
                     env_extra={guard_context_budget.ENV_AUTO: "1"})
    assert block.returncode == 2, f"Auto-Modus muss blocken: {block.returncode}"
    for teil in ("/handoff", "/clear", "/resume"):
        assert nennt_befehl(block.stderr, teil), f"{teil} fehlt im Block-Zweig: {block.stderr}"
    assert "rollover" not in block.stderr.lower(), block.stderr


TESTS = [
    test_unter_schwelle_bleibt_still,
    test_ueber_schwelle_warnt_einmal,
    test_zweiter_turn_derselben_sitzung_still,
    test_neue_sitzung_warnt_wieder,
    test_env_schwelle_greift,
    test_kaputte_env_schwelle_faellt_auf_default,
    test_summe_ueber_alle_usage_felder,
    test_sidechain_zeile_zaehlt_nicht,
    test_auto_modus_warnt_in_jedem_turn,
    test_auto_modus_still_wenn_brief_im_turn_geschrieben,
    test_auto_modus_ignoriert_brief_aus_altem_turn,
    test_auto_modus_nennt_treiber_weg_bei_marker,
    test_meldung_nennt_manuellen_weg_und_keinen_rollover,
    test_loop_schutz_und_subagent_still,
    test_fail_open_pfade,
]


def main() -> int:
    failures = []
    for test in TESTS:
        try:
            with tempfile.TemporaryDirectory() as tmp:
                test(tmp)
        except Exception as exc:
            failures.append(f"FAIL {test.__name__}: {exc}")
        else:
            print(f"ok   {test.__name__}")
    for line in failures:
        print(line, file=sys.stderr)
    print(f"\n{len(TESTS) - len(failures)}/{len(TESTS)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
