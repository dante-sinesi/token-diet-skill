"""One fact, one place: line caps per document, repetition between documents, and loss when text moves.

Usage:
  python texto.py check [PATH ...] [--root DIR] [--min-chars N] [--json]
  python texto.py compare OLD NEW [--json]

check    flags documents above their line cap and paragraphs repeated in more than one document.
         Caps come from .token-diet/config.json ("document_limits": {"docs/*.md": 300}) as path
         patterns; with none configured only repetition is checked.
compare  says what the old text had that the new text lost: headings, inline code, URLs, paths and
         numbers. Use it after moving or trimming a document.

A document with "token-diet-ignore" in its first 5 lines is skipped; a paragraph containing it is not
compared. Exit codes: 0 nothing found, 1 something found, 2 bad usage.
"""
import argparse
import fnmatch
import json
import pathlib
import re
import sys

import modo
import version
import walk

DOC_EXTS = {".md", ".markdown", ".txt", ".rst"}
MARKER = "token-diet-ignore"
MIN_CHARS = 120
URL = re.compile(r"https?://[^\s)>\]]+")
CODE_SPAN = re.compile(r"`([^`\n]{2,60})`")
NUMBER = re.compile(r"(?<![\w.])\d[\d.,]*\d(?![\w])|(?<![\w.])\d{2,}(?![\w])")
PATHLIKE = re.compile(r"(?<![\w/.])(?:[\w.-]+/)+[\w.-]+")


def _documents(paths, root):
    for base in paths:
        for path in walk.iter_files(base):
            if path.suffix.lower() in DOC_EXTS and walk.is_text(path):
                text = walk.read_text(path)
                if any(MARKER in line for line in text.splitlines()[:5]):
                    continue
                yield walk.relative(path, root), text


def _paragraphs(text):
    block, start = [], 1
    for number, line in enumerate(text.splitlines() + [""], 1):
        if line.strip():
            if not block:
                start = number
            block.append(line)
        elif block:
            joined = " ".join(" ".join(block).lower().split())
            if MARKER not in joined and not joined.startswith(("```", "|", "#")):
                yield start, joined
            block = []


def check(paths, root, min_chars=MIN_CHARS):
    root = pathlib.Path(root).resolve()
    limits = modo.load_config(root)["document_limits"]
    over, seen = [], {}
    for rel, text in _documents(paths, root):
        count = len(text.splitlines())
        for pattern, cap in limits.items():
            if fnmatch.fnmatch(rel, pattern) and count > cap:
                over.append({"file": rel, "lines": count, "cap": cap, "pattern": pattern})
                break
        for start, paragraph in _paragraphs(text):
            if len(paragraph) >= min_chars:
                seen.setdefault(paragraph, []).append((rel, start))
    repeated = []
    for paragraph, places in seen.items():
        if len({f for f, _ in places}) >= 2:
            repeated.append({"chars": len(paragraph), "preview": paragraph[:70], "places": [f"{f}:{n}" for f, n in places]})
    repeated.sort(key=lambda r: -r["chars"] * len(r["places"]))
    return {"over_cap": over, "repeated": repeated}


def _facts(text):
    text = "\n".join(line for line in text.splitlines() if MARKER not in line)
    return {
        "headings": {l.strip().lstrip("#").strip() for l in text.splitlines() if re.match(r"^\s{0,3}#{1,6}\s", l)},
        "code": set(CODE_SPAN.findall(text)),
        "urls": set(URL.findall(text)),
        "paths": set(PATHLIKE.findall(URL.sub("", text))),
        "numbers": set(NUMBER.findall(text)),
    }


def compare(old, new):
    before, after = _facts(old), _facts(new)
    return {kind: sorted(before[kind] - after[kind]) for kind in before if before[kind] - after[kind]}


def render_check(report):
    if not report["over_cap"] and not report["repeated"]:
        return "No document over its cap and no paragraph repeated between documents."
    lines = []
    for item in report["over_cap"]:
        lines.append(f"over cap: {item['file']} has {item['lines']} lines (cap {item['cap']} for {item['pattern']})")
    for item in report["repeated"][:15]:
        lines.append(f"repeated ({item['chars']} chars): \"{item['preview']}...\" in {', '.join(item['places'])}")
    if len(report["repeated"]) > 15:
        lines.append(f"... {len(report['repeated']) - 15} more repeated paragraphs")
    return "\n".join(lines)


def render_compare(report):
    if not report:
        return "Nothing lost: every heading, inline code, URL, path and number of the old text is in the new one."
    return "\n".join(f"lost {kind}: {', '.join(values[:12])}" + (f" (+{len(values) - 12} more)" if len(values) > 12 else "")
                     for kind, values in report.items())


def main(argv):
    parser = argparse.ArgumentParser(description="Line caps, repetition and information-loss checks for documents.")
    parser.add_argument("--version", action="version", version=version.label())
    parser.add_argument("command", choices=["check", "compare"])
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--root")
    parser.add_argument("--min-chars", type=int, default=MIN_CHARS)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "compare":
        if len(args.paths) != 2:
            print("error: compare needs OLD and NEW", file=sys.stderr)
            return 2
        report = compare(walk.read_text(args.paths[0]), walk.read_text(args.paths[1]))
        print(json.dumps(report, indent=1) if args.json else render_compare(report))
        return 1 if report else 0
    root = pathlib.Path(args.root).resolve() if args.root else modo.project_root()
    report = check(args.paths or [root], root, args.min_chars)
    print(json.dumps(report, indent=1) if args.json else render_check(report))
    return 1 if report["over_cap"] or report["repeated"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
