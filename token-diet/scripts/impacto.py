"""Finds where a symbol is defined and used, and whether something similar already exists.

Usage: python impacto.py SYMBOL [--root DIR] [--max-files N] [--json]
       python impacto.py --exists WORD [WORD ...] [--root DIR] [--max-files N] [--json]

Answers three questions without opening files: where is it defined, who uses it (files,
counts, line numbers and the first use of each file), and is there already a definition
with a similar name (so you reuse it instead of writing another one).
Matching is textual (whole word), so it works in any language, and may include comments
or strings that mention the name.

--exists WORDS answers "does something like this already exist?" before writing a new one: it lists the
definitions whose names share words with WORDS (camelCase and snake_case are split, accents and
plurals are ignored), best match first.
"""
import argparse
import difflib
import unicodedata
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import version  # noqa: E402
import walk  # noqa: E402

DEF_KEYWORDS = r"(?:def|class|function|func|fn|interface|struct|enum|trait|type|sub|module|const|let|var)"
DEFINED_NAME = re.compile(r"^\s*(?:export\s+|public\s+|private\s+|protected\s+|static\s+|async\s+|abstract\s+)*" + DEF_KEYWORDS + r"\s+([A-Za-z_$][\w$]*)")
ASSIGNED_FUNCTION = re.compile(r"^\s*(?:export\s+)?([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:function\b|\([^)]*\)\s*=>)")


def _words(name):
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name).replace("_", " ").replace("-", " ")
    return {w.lower() for w in spaced.split() if w}


def _similar(a, b):
    if a == b:
        return False
    wa, wb = _words(a), _words(b)
    overlap = len(wa & wb) / len(wa | wb) if wa and wb else 0
    return overlap >= 0.5 or difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio() >= 0.8


def _fold(word):
    """Lowercase, no accents, no trailing plural: so `tarjetas` finds `leer_tarjeta`."""
    word = "".join(c for c in unicodedata.normalize("NFKD", word.lower()) if not unicodedata.combining(c))
    for suffix in ("es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[: -len(suffix)]
    return word


def _name_words(name):
    return {_fold(w) for w in _words(name)} | {_fold(name)}


def find_existing(root, words, limit=15):
    """Definitions whose names share at least one word with `words`, ranked by how many they share."""
    wanted = {_fold(w) for part in words for w in _words(part) or {part.lower()} if len(w) >= 3}
    root = pathlib.Path(root)
    found = {}
    for path in walk.iter_files(root):
        if not walk.is_text(path):
            continue
        rel = walk.relative(path, root)
        for number, line in enumerate(walk.read_text(path).splitlines(), 1):
            name = defined_name(line)
            if not name:
                continue
            shared = wanted & _name_words(name)
            if shared and (name, rel) not in found:
                found[(name, rel)] = {"name": name, "at": f"{rel}:{number}", "shared": sorted(shared), "line": line.strip()[:100]}
    ranked = sorted(found.values(), key=lambda m: (-len(m["shared"]), m["name"].lower(), m["at"]))
    return {"words": sorted(wanted), "matches": ranked[:limit], "total": len(ranked)}


def render_existing(report):
    if not report["matches"]:
        return f"Nothing similar is defined for: {', '.join(report['words'])}. Safe to write a new one."
    lines = [f"{report['total']} definitions share words with: {', '.join(report['words'])}"]
    for match in report["matches"]:
        lines.append(f"  {match['name']}  {match['at']}  (shares: {', '.join(match['shared'])})")
    if report["total"] > len(report["matches"]):
        lines.append(f"  ... {report['total'] - len(report['matches'])} more")
    return "\n".join(lines)


def defined_name(line):
    match = DEFINED_NAME.match(line) or ASSIGNED_FUNCTION.match(line)
    return match.group(1) if match else None


def analyze(root, symbol, max_files=15):
    root = pathlib.Path(root)
    pattern = re.compile(r"(?<![\w$])" + re.escape(symbol) + r"(?![\w$])")
    definitions, usage, similar = [], {}, {}
    for path in walk.iter_files(root):
        if not walk.is_text(path):
            continue
        rel = walk.relative(path, root)
        for number, line in enumerate(walk.read_text(path).splitlines(), 1):
            name = defined_name(line)
            if name and name != symbol and _similar(symbol, name):
                similar.setdefault(name, f"{rel}:{number}")
            if not pattern.search(line):
                continue
            if name == symbol:
                definitions.append({"at": f"{rel}:{number}", "line": line.strip()[:120]})
            else:
                entry = usage.setdefault(rel, {"count": 0, "lines": [], "first": line.strip()[:100]})
                entry["count"] += 1
                if len(entry["lines"]) < 12:
                    entry["lines"].append(number)
    files = sorted(usage.items(), key=lambda item: -item[1]["count"])
    return {
        "symbol": symbol,
        "definitions": definitions,
        "files_using": len(usage),
        "uses": sum(entry["count"] for _, entry in files),
        "usage": [{"file": f, **entry} for f, entry in files[:max_files]],
        "files_not_listed": max(0, len(files) - max_files),
        "similar": [{"name": n, "at": at} for n, at in sorted(similar.items())[:10]],
    }


def render(report):
    lines = [f"Symbol: {report['symbol']}"]
    if report["definitions"]:
        lines += [f"Defined: {d['at']}  {d['line']}" for d in report["definitions"]]
    else:
        lines.append("Defined: no definition found in this project (to look for names that contain the word, use --exists WORD)")
    lines.append(f"Used in {report['files_using']} files ({report['uses']} places):")
    for item in report["usage"]:
        lines.append(f"  {item['file']} ({item['count']}): lines {', '.join(map(str, item['lines']))}  | {item['first']}")
    if report["files_not_listed"]:
        lines.append(f"  ... {report['files_not_listed']} more files")
    if report["similar"]:
        lines.append("Similar names already defined: " + ", ".join(f"{s['name']} ({s['at']})" for s in report["similar"]))
    return "\n".join(lines)


def main(argv):
    parser = argparse.ArgumentParser(description="Find the definition and uses of a symbol.")
    parser.add_argument("--version", action="version", version=version.label())
    parser.add_argument("symbol", nargs="+", help="a symbol (or, with --exists, words)")
    parser.add_argument("--exists", action="store_true", help="list definitions whose names share words with the arguments")
    parser.add_argument("--root", default=".")
    parser.add_argument("--max-files", type=int, default=15)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.exists:
        report = find_existing(args.root, args.symbol, args.max_files)
        print(json.dumps(report, indent=1) if args.json else render_existing(report))
        return 0
    if len(args.symbol) != 1:
        parser.error("give one symbol, or use --exists with several words")
    report = analyze(args.root, args.symbol[0], args.max_files)
    print(json.dumps(report, indent=1) if args.json else render(report))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
