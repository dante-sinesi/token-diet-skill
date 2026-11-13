"""Runs a test, linter or build command and returns only the lines that matter.

Usage: python resumir.py [--max-lines N] [--timeout SECONDS] [--out DIR] -- COMMAND [ARGS ...]

Prints the exit code, the duration and, when something failed or warned, those lines with
one line of context (traceback frames included) plus the closing summary. A clean run is
one line plus the summary. The complete output is saved to --out (default
.token-diet/runs) and the report says where, so the detail is read by ranges only when
needed. The exit code of the command is returned.
"""
import argparse
import hashlib
import math
import pathlib
import re
import subprocess
import sys
import time

import guard
import modo
import terminal
import version

PROBLEM = re.compile(
    r"(\bFAIL(?:ED|URE|S)?\b|\bERROR(?:S)?\b|\bFatal\b|Traceback \(most recent call last\)|AssertionError|\bpanic\b|"
    r"error[:\[ ]|\bwarning\b|\bWARN\b|\bException\b|✗|✖|npm ERR!|Cannot find|not found|undefined reference)",
    re.I,
)
SUMMARY = re.compile(r"(\d+\s+(passed|failed|errors?|warnings?|tests?)|\bOK\b|Ran \d+ tests?|Build (succeeded|failed)|Finished|Tests:|Test Suites:|error summary|problems?\b)", re.I)
TAIL = 4
MAX_LINES = 500_000


def tokens(text):
    return math.ceil(len(text) / 4)


def pick(lines, max_lines):
    keep = set()
    for index, line in enumerate(lines):
        if PROBLEM.search(line) or terminal.is_important(line):
            keep.update(range(max(0, index - 1), min(len(lines), index + 2)))
            nxt = index + 1
            while nxt < len(lines) and lines[nxt][:1] in (" ", "\t"):
                keep.add(nxt)
                nxt += 1
    for index, line in enumerate(lines):
        if index >= len(lines) - TAIL or (SUMMARY.search(line) and index >= len(lines) - 15):
            keep.add(index)
    chosen = sorted(keep)
    truncated = max(0, len(chosen) - max_lines)
    if truncated:
        chosen = chosen[: max_lines // 2] + chosen[-(max_lines - max_lines // 2):]
    out, last = [], None
    for index in chosen:
        if last is not None and index != last + 1:
            out.append("...")
        out.append(lines[index])
        last = index
    return out, truncated


def run(command, timeout=600):
    start = time.time()
    try:
        done = subprocess.run(command, capture_output=True, timeout=timeout)
        text = (done.stdout or b"").decode("utf-8", errors="replace") + (done.stderr or b"").decode("utf-8", errors="replace")
        return done.returncode, text.replace("\r\n", "\n"), time.time() - start
    except FileNotFoundError:
        return 127, f"command not found: {command[0]}", time.time() - start
    except subprocess.TimeoutExpired as error:
        partial = error.stdout or ""
        if isinstance(partial, bytes):
            partial = partial.decode("utf-8", errors="replace")
        return 124, partial + f"\ntimed out after {timeout}s", time.time() - start


def summarize(command, code, output, seconds, max_lines, out_dir):
    lines = [terminal.clean_line(line) for line in terminal.lines_of(output)]
    skipped = max(0, len(lines) - MAX_LINES)
    lines = lines[skipped:]
    digest = hashlib.sha256(output.encode("utf-8", errors="replace")).hexdigest()[:8]
    target = pathlib.Path(out_dir) / f"{pathlib.Path(command[0]).stem}-{digest}.log"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(output, encoding="utf-8")
    shown, truncated = pick(lines, max_lines)
    head = f"exit {code}, {len(lines) + skipped} lines (~{tokens(output):,} tokens) -> full output: {target}"
    if skipped:
        head += f" (only the last {MAX_LINES:,} lines were scanned)"
    body = "\n".join(shown)
    report = head + ("\n" + body if body else "")
    if truncated:
        report += f"\n... {truncated} more relevant lines in the full output"
    return report, target


def main(argv):
    if argv[:1] == ["--version"]:
        print(version.label())
        return 0
    if "--" not in argv:
        print("usage: resumir.py [--max-lines N] [--timeout S] [--out DIR] -- COMMAND [ARGS ...]", file=sys.stderr)
        return 2
    split = argv.index("--")
    parser = argparse.ArgumentParser(description="Run a command and return only the lines that matter.")
    parser.add_argument("--max-lines", type=int, default=60)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--out", default=".token-diet/runs")
    args = parser.parse_args(argv[:split])
    command = argv[split + 1:]
    if not command:
        print("error: no command after --", file=sys.stderr)
        return 2
    code, output, seconds = run(command, args.timeout)
    report, target = summarize(command, code, output, seconds, args.max_lines, args.out)
    if not guard.never_worse(output, report, modo.profile_value(modo.project_root(), "min_gain")):
        target.unlink(missing_ok=True)
        print(output.rstrip("\n"))
        return code
    print(report)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
