"""Reports comment noise: comments that say what the code already says, commented-out code, decoration.

Usage: python comentarios.py [PATH ...] [--ext py,js,...] [--max N] [--json]

Only the why earns a comment. This tool reports and never edits. It skips shebangs, encodings,
licenses, TODO/FIXME/NOTE/HACK, linter and type directives, and anything with "token-diet-ignore" on
the comment or on the code line below it. Exit codes: 0 nothing found, 1 something found.
"""
import argparse
import json
import pathlib
import re
import sys

import version
import walk

PREFIX = {
    ".py": "#", ".sh": "#", ".rb": "#", ".yml": "#", ".yaml": "#", ".toml": "#",
    ".js": "//", ".jsx": "//", ".ts": "//", ".tsx": "//", ".php": "//", ".go": "//", ".java": "//", ".c": "//", ".h": "//",
    ".cpp": "//", ".cs": "//", ".rs": "//", ".swift": "//", ".kt": "//", ".sql": "--",
}
MARKER = "token-diet-ignore"
KEEP = re.compile(
    r"(todo|fixme|hack|xxx|note:|copyright|license|licence|noqa|type:|pragma|eslint|pylint|istanbul|region|endregion|"
    r"coding[:=]|shebang|nolint|prettier|ts-ignore|ts-expect-error|mypy|pyright|rubocop|why|because|so that|workaround)", re.I)
STOP = set("the a an and or of to in on for with is are be this that it as at by from not no if into then so we you".split())
CODE_LIKE = re.compile(r"^\s*(def|class|if|elif|else|for|while|return|import|from|print|var|let|const|function|echo|try|except)\b.*[:({;]\s*$"
                       r"|^\s*[\w.\[\]]+\s*(=|\+=|-=)\s*[^=].*[;)]?\s*$|[;{}]\s*$|^\s*\w+\(.*\)\s*;?\s*$")
DECORATION = re.compile(r"^[\W_]{4,}$")


def _words(text):
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text.replace("_", " "))
    return {w.lower() for w in re.findall(r"[A-Za-z]{3,}", spaced) if w.lower() not in STOP}


def _stem(word):
    for suffix in ("ing", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def _stems(words):
    return {_stem(w) for w in words}


def analyze(path):
    prefix = PREFIX.get(pathlib.Path(path).suffix.lower())
    if not prefix:
        return []
    lines = walk.read_text(path).splitlines()
    found = []
    for index, raw in enumerate(lines):
        stripped = raw.strip()
        if not stripped.startswith(prefix) or stripped.startswith("#!"):
            continue
        body = stripped[len(prefix):].strip()
        following = next((l for l in lines[index + 1:index + 4] if l.strip() and not l.strip().startswith(prefix)), "")
        if MARKER in body or MARKER in following:
            continue
        if not body:
            continue
        if DECORATION.match(body):
            found.append({"line": index + 1, "kind": "decoration", "text": body[:60]})
            continue
        if KEEP.search(body):
            continue
        if CODE_LIKE.search(body) and not re.search(r"[A-Za-z]{3,}\s+[A-Za-z]{3,}\s+[A-Za-z]{3,}\s+[A-Za-z]{3,}", body):
            found.append({"line": index + 1, "kind": "commented-out code", "text": body[:60]})
            continue
        words = _stems(_words(body))
        code_words = _stems(_words(following))
        if len(words) >= 2 and len(body.split()) <= 6 and len(words & code_words) / len(words) >= 0.5:
            found.append({"line": index + 1, "kind": "says what the code says", "text": body[:60]})
    return found


def scan(paths, extensions=None):
    results = {}
    root = pathlib.Path(paths[0]) if paths else pathlib.Path(".")
    for base in paths:
        anchor = pathlib.Path(base) if pathlib.Path(base).is_dir() else pathlib.Path(base).parent
        for path in walk.iter_files(base):
            if extensions and path.suffix.lstrip(".").lower() not in extensions:
                continue
            if path.suffix.lower() in PREFIX and walk.is_text(path):
                items = analyze(path)
                if items:
                    results[walk.relative(path, anchor)] = items
    return results


def render(results, limit):
    if not results:
        return "No comment noise found."
    total = sum(len(v) for v in results.values())
    lines = [f"{total} comments in {len(results)} files:"]
    shown = 0
    for rel, items in sorted(results.items()):
        for item in items:
            if shown >= limit:
                break
            lines.append(f"  {rel}:{item['line']}  {item['kind']}: {item['text']}")
            shown += 1
    if total > shown:
        lines.append(f"  ... {total - shown} more")
    return "\n".join(lines)


def main(argv):
    parser = argparse.ArgumentParser(description="Report comment noise.")
    parser.add_argument("--version", action="version", version=version.label())
    parser.add_argument("paths", nargs="*", default=["."])
    parser.add_argument("--ext")
    parser.add_argument("--max", type=int, default=40)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    extensions = {e.strip().lstrip(".").lower() for e in args.ext.split(",")} if args.ext else None
    results = scan(args.paths, extensions)
    print(json.dumps(results, indent=1) if args.json else render(results, args.max))
    return 1 if results else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
