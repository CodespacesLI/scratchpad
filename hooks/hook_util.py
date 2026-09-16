#!/usr/bin/env python3
"""Gemeinsame Helfer der beiden Stop-Wächter.

Bewusst winzig und ohne Abhängigkeiten ausser der Python-Standardbibliothek: die
Wächter sollen einzeln kopierbar bleiben. Enthalten ist nur, was die Wächter wirklich
brauchen.

* `iter_lines_reverse(path)` — liest eine Transcript-Datei rückwärts vom Ende her.
  Transcripts werden gross; ein Wächter, der die ganze Datei einliest, wird mit der
  Sitzungsdauer langsamer. Rückwärts lesen findet die Turn-Grenze nach wenigen
  Kilobyte.
* `is_subagent_stop(data)` — erkennt, ob ein Stop-Ereignis aus einem Subagenten kommt.
  Die Warnungen der Stop-Wächter adressieren den Hauptthread; im Subagenten wären sie
  Rauschen an der falschen Stelle.
* `use_utf8_stdio()` — stellt stdin, stdout und stderr auf UTF-8 um. Claude Code spricht
  mit den Hooks in UTF-8; Python nimmt unter Windows ohne Zutun die Landes-Codepage
  (cp1252). Eine Meldung mit Umlauten käme sonst als Zeichensalat an.
"""
from __future__ import annotations

import os
import sys

# Rückwärts-Lesen in Blöcken: gross genug, dass eine Turn-Grenze meist im ersten
# Block liegt, klein genug, dass nie die ganze Datei im Speicher steht.
_CHUNK = 64 * 1024

# Signale, an denen ein Subagenten-Transcript erkennbar ist.
_SUBAGENT_DIR_SEGMENT = "/subagents/"
_SUBAGENT_FILE_PREFIX = "agent-"


def _decode_line(line: bytes) -> str:
    """Rohe Zeile -> str, ohne Zeilenende-Rest.

    Gelesen wird binär (`rb`), also übersetzt kein Textmodus die Zeilenenden. Ein
    Transcript, das unter Windows mit CRLF geschrieben wurde, lässt nach dem Split an
    `\\n` ein `\\r` stehen — das gehört zum Trenner, nicht zum Inhalt.
    """
    return line.rstrip(b"\r").decode("utf-8", "replace")


def iter_lines_reverse(path):
    """Zeilen der Datei vom Ende her, leere Zeilen übersprungen."""
    with open(path, "rb") as fh:
        fh.seek(0, os.SEEK_END)
        pos = fh.tell()
        tail = b""
        while pos > 0:
            size = min(_CHUNK, pos)
            pos -= size
            fh.seek(pos)
            buf = fh.read(size) + tail
            lines = buf.split(b"\n")
            tail = lines.pop(0)  # kann eine halbe Zeile sein — nächster Block ergänzt sie
            for line in reversed(lines):
                if line.strip():
                    yield _decode_line(line)
        if tail.strip():
            yield _decode_line(tail)


def is_subagent_stop(data) -> bool:
    """True, wenn dieser Stop im Kontext eines Subagenten feuert.

    Robust gegen jeden Input: Nicht-Dict, fehlende oder leere Felder, Nicht-String-Pfade
    ergeben False. Wirft nie.
    """
    if not isinstance(data, dict):
        return False
    if data.get("agent_id") or data.get("agent_type"):
        return True
    path = data.get("transcript_path")
    if isinstance(path, str) and path:
        norm = path.replace("\\", "/")
        base = norm.rsplit("/", 1)[-1]
        if _SUBAGENT_DIR_SEGMENT in norm or base.startswith(_SUBAGENT_FILE_PREFIX):
            return True
    return False


def use_utf8_stdio() -> None:
    """Standard-Ströme auf UTF-8 stellen; wirft nie.

    Muss vor dem ersten Lesen bzw. Schreiben laufen. `errors="replace"` statt Abbruch:
    ein nicht kodierbares Zeichen (z.B. ein einzelnes Surrogat aus einem Pfad) darf die
    Meldung nicht kosten. Ein Strom ohne `reconfigure` (ersetzt, umgeleitet) bleibt, wie
    er ist.
    """
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
