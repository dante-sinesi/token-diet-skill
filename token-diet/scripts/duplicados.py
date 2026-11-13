"""Detects repeated blocks of code, so the same thing is not read (or written) twice.

Usage: python duplicados.py [PATH ...] [--min-lines N] [--max N] [--ext py,js,...] [--json]

A block is a run of at least --min-lines (default 6) significant lines that appears in
two or more places. Whitespace differences and blank or punctuation-only lines are
ignored; names are compared as written, so renamed copies are not reported.
"""
import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import version  # noqa: E402
import walk  # noqa: E402

TRIVIAL = re.compile(r"^[\W_]*$")


def _significant(path):
    lines = []
    for number, raw in enumerate(walk.read_text(path).splitlines(), 1):
        text = " ".join(raw.split())
        if len(text) >= 4 and not TRIVIAL.match(text):
            lines.append((number, text))
    return lines


def find(paths, min_lines=6, extensions=None):
    sources = {}
    for raw in paths:
        base = pathlib.Path(raw)
        anchor = base if base.is_dir() else base.parent
        for path in walk.iter_files(base):
            if not walk.is_text(path) or walk.language_of(path) not in walk.CODE_LANGUAGES:
                continue
            if extensions and path.suffix.lstrip(".").lower() not in extensions:
                continue
            sig = _significant(path)
            if len(sig) >= min_lines:
                sources[walk.relative(path, anchor)] = sig
    windows = {}
    for name, sig in sources.items():
        for i in range(len(sig) - min_lines + 1):
            key = tuple(t for _, t in sig[i:i + min_lines])
            windows.setdefault(key, []).append((name, i))
    keyed = {}
    for key, places in windows.items():
        if len(places) >= 2:
            for place in places:
                keyed[place] = key
    covered, blocks = set(), []
    for name, sig in sources.items():
        for i in range(len(sig) - min_lines + 1):
            if (name, i) in covered or (name, i) not in keyed:
                continue
            places = windows[keyed[(name, i)]]
            extra = 0
            while (name, i + extra + 1) in keyed and all(
                (n, j + extra + 1) in keyed and keyed[(n, j + extra + 1)] == keyed[(name, i + extra + 1)]
                for n, j in places
            ):
                extra += 1
            for n, j in places:
                covered.update((n, j + k) for k in range(extra + 1))
            length = min_lines + extra
            blocks.append({
                "lines": length,
                "places": [
                    {"file": n, "from": sources[n][j][0], "to": sources[n][j + length - 1][0]} for n, j in places
                ],
            })
    return sorted(blocks, key=lambda b: (-b["lines"] * len(b["places"]), b["places"][0]["file"]))


def render(blocks, limit):
    if not blocks:
        return "No repeated blocks found."
    lines = [f"{len(blocks)} repeated blocks (largest first):"]
    for block in blocks[:limit]:
        where = ", ".join(f"{p['file']}:{p['from']}-{p['to']}" for p in block["places"])
        lines.append(f"  {block['lines']} lines x{len(block['places'])}: {where}")
    if len(blocks) > limit:
        lines.append(f"  ... {len(blocks) - limit} more")
    return "\n".join(lines)


def main(argv):
    parser = argparse.ArgumentParser(description="Detect repeated blocks of code.")
    parser.add_argument("--version", action="version", version=version.label())
    parser.add_argument("paths", nargs="*", default=["."])
    parser.add_argument("--min-lines", type=int, default=6)
    parser.add_argument("--max", type=int, default=15)
    parser.add_argument("--ext")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    extensions = {e.strip().lstrip(".").lower() for e in args.ext.split(",")} if args.ext else None
    blocks = find(args.paths, max(2, args.min_lines), extensions)
    print(json.dumps(blocks, indent=1) if args.json else render(blocks, args.max))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
