"""Terminal-output cleanup shared by compactar.py and resumir.py.

Not a command. Lines are split on the line feed only, so line numbers always match the original
file; each line is cleaned on its own: ANSI control sequences are removed (display noise) and a
carriage-return progress redraw collapses to its last visible state.
"""
import re

ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b[@-Z\\-_]")
IMPORTANT = re.compile(
    r"(\b(ERROR|ERR|FATAL|PANIC|EXCEPTION|TRACEBACK|FAIL|FAILED|FAILURE|WARN|WARNING|CRITICAL)\b"
    r"|\b[A-Za-z]+(Error|Exception)\b"
    r"|^\s+at\s|^\s+File \""
    r"|\.go:\d+"
    r"|\S:\d+:\d+"
    r"|exit status [1-9]|exited with code [1-9]|exit code [1-9]|returned non-zero)",
    re.I,
)


def lines_of(text):
    """Lines split on the line feed only (so numbers match the original); no trailing empty line."""
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def clean_line(line):
    """One line without ANSI sequences and with progress redraws collapsed to the last visible state."""
    if "\r" in line:
        parts = [p for p in line.rstrip("\r").split("\r") if p.strip()]
        line = parts[-1] if parts else ""
    return ANSI.sub("", line)


def is_important(line):
    """Signal that must never be elided: errors, camelCase error types, locations, non-zero exits."""
    return bool(IMPORTANT.search(line))
