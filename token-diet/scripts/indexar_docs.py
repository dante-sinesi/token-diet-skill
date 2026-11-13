"""Index and concept map of a project, so a question is answered without opening files.

Usage:
  python indexar_docs.py build [PATH ...] [--root DIR]
  python indexar_docs.py query TERM [TERM ...] [--limit N] [--root DIR]
  python indexar_docs.py note show [--quiet] | write [--text TEXT] [--root DIR]     (write reads stdin without --text)

build   indexes documents (Markdown and text: every section with its line range) and the
        functions and classes of code files, plus links between documents. The index lives
        in <root>/.token-diet/index/ (graph.json for tools, index.md to read). Only changed
        files are re-read.
query   ranks the sections and symbols that answer the terms and, for each one, says the
        tokens of opening that section and the whole file, so you open only what is worth it.
note    the continuity note: one file (.token-diet/continuity.md) with a token cap, so a new
        session continues without re-explaining the project. Writing over the cap fails.
        "show --quiet" prints nothing when there is no note (what the session-start hook uses).

Without --root the project is $CLAUDE_PROJECT_DIR or the current folder.

A line containing "token-diet-ignore" is left out of the concepts; a document with that
marker in its first 5 lines is not indexed. Tokens are characters / 4.
Exit codes: 0 ok, 1 error (no index, note over the cap, bad usage).
"""
import argparse
import hashlib
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import version  # noqa: E402
import impacto  # noqa: E402
import modo  # noqa: E402
import walk  # noqa: E402

MARKER = "token-diet-ignore"
DOC_EXTS = {".md", ".markdown", ".txt"}
NOTE_MAX_TOKENS = 800
STOPWORDS = set("the a an and or of to in on for with is are be this that it as at by from not no if into than then so but how what when where which who why do does can will should use used using you your we our their its".split())
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
BACKTICK = re.compile(r"`([^`\n]{2,40})`")
TERMS_PER_ENTRY = 14


def index_dir(root):
    return pathlib.Path(root) / ".token-diet" / "index"


def note_path(root):
    return pathlib.Path(root) / ".token-diet" / "continuity.md"


def words(text, minimum=3):
    found = re.findall(r"[A-Za-z][A-Za-z0-9]+", re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text.replace("_", " ")))
    return [w.lower() for w in found if len(w) >= minimum and w.lower() not in STOPWORDS]


def _terms(heading, body):
    terms = list(dict.fromkeys(words(heading)))
    for span in BACKTICK.findall(body):
        terms.append(span.strip().lower())
    counts = {}
    for word in words(body, 4):
        counts[word] = counts.get(word, 0) + 1
    terms += [w for w, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:TERMS_PER_ENTRY]]
    return list(dict.fromkeys(terms))[:TERMS_PER_ENTRY * 2]


def _tokens(lines):
    return walk.tokens(sum(len(line) + 1 for line in lines))


def parse_document(rel, text):
    lines = text.splitlines()
    if any(MARKER in line for line in lines[:5]):
        return [], []
    headings, in_fence = [], False
    for number, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        match = None if in_fence else HEADING.match(line)
        if match and MARKER not in line:
            headings.append((number, len(match.group(1)), match.group(2)))
    entries = []
    if not headings:
        entries.append({"file": rel, "kind": "section", "title": pathlib.PurePosixPath(rel).name, "level": 0, "start": 1,
                        "end": len(lines), "tokens": _tokens(lines), "terms": _terms(rel, text)})
    if headings and headings[0][0] > 1:
        headings.insert(0, (1, 0, pathlib.PurePosixPath(rel).name))
    for index, (start, level, title) in enumerate(headings):
        end = len(lines)
        for later_start, later_level, _ in headings[index + 1:]:
            if later_level <= level or level == 0:
                end = later_start - 1
                break
        body_lines = [l for l in lines[start:end] if MARKER not in l]
        entries.append({"file": rel, "kind": "section", "title": title, "level": level, "start": start, "end": end,
                        "tokens": _tokens(lines[start - 1:end]), "terms": _terms(title, "\n".join(body_lines))})
    links = []
    for match in LINK.findall(text):
        target = match.strip()
        if "://" in target or target.startswith(("mailto:", "#")):
            continue
        resolved = pathlib.PurePosixPath(rel).parent.joinpath(target)
        parts = []
        for part in resolved.parts:
            if part == "..":
                if parts:
                    parts.pop()
            elif part != ".":
                parts.append(part)
        links.append("/".join(parts))
    return entries, links


def parse_code(rel, text):
    lines = text.splitlines()
    found = []
    for number, line in enumerate(lines, 1):
        name = impacto.defined_name(line)
        if name and len(name) >= 3 and MARKER not in line:
            found.append((number, name))
    entries = []
    for index, (start, name) in enumerate(found):
        end = found[index + 1][0] - 1 if index + 1 < len(found) else len(lines)
        entries.append({"file": rel, "kind": "symbol", "title": name, "level": 0, "start": start, "end": end,
                        "tokens": _tokens(lines[start - 1:end]), "terms": list(dict.fromkeys(words(name)))})
    return entries


def _signature(path):
    stat = path.stat()
    return f"{stat.st_size}:{stat.st_mtime_ns}"


def build(root, paths=None):
    root = pathlib.Path(root).resolve()
    target = index_dir(root)
    previous = {}
    try:
        previous = json.loads((target / "graph.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pass
    old_files, old_entries, old_links = previous.get("files", {}), previous.get("entries", []), previous.get("links", {})
    files, entries, links, reused = {}, [], {}, 0
    for base in [pathlib.Path(p) for p in (paths or [root])]:
        for path in walk.iter_files(base):
            suffix = path.suffix.lower()
            is_doc = suffix in DOC_EXTS
            is_code = walk.language_of(path) in walk.CODE_LANGUAGES
            if not (is_doc or is_code) or not walk.is_text(path):
                continue
            rel = walk.relative(path, root)
            signature = _signature(path)
            text = None
            if rel in old_files and old_files[rel]["sig"] == signature:
                reused += 1
                found = [e for e in old_entries if e["file"] == rel]
                links[rel] = old_links.get(rel, [])
                files[rel] = old_files[rel]
            else:
                text = walk.read_text(path)
                found, file_links = parse_document(rel, text) if is_doc else (parse_code(rel, text), [])
                links[rel] = file_links
                files[rel] = {"sig": signature, "tokens": walk.tokens(len(text)), "hash": hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:12]}
            entries.extend(found)
    graph = {"files": files, "entries": entries, "links": {k: v for k, v in links.items() if v}}
    target.mkdir(parents=True, exist_ok=True)
    (target / "graph.json").write_text(json.dumps(graph, separators=(",", ":")), encoding="utf-8")
    (target / "index.md").write_text(render_index(graph), encoding="utf-8")
    return {"files": len(files), "entries": len(entries), "reused": reused}


def render_index(graph):
    lines = ["# Index (generated; do not edit)", "", "file (tokens): sections with line ranges", ""]
    by_file = {}
    for entry in graph["entries"]:
        by_file.setdefault(entry["file"], []).append(entry)
    for rel, entries in sorted(by_file.items()):
        lines.append(f"{rel} (~{graph['files'][rel]['tokens']:,})")
        for entry in entries[:40]:
            mark = "  " * max(0, entry["level"] - 1) + ("fn " if entry["kind"] == "symbol" else "")
            lines.append(f"  {mark}{entry['title']} [{entry['start']}-{entry['end']}] ~{entry['tokens']:,}")
    return "\n".join(lines) + "\n"


def load(root):
    try:
        return json.loads((index_dir(root) / "graph.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def stale_files(root, graph):
    root = pathlib.Path(root).resolve()
    changed = []
    for rel, meta in graph["files"].items():
        path = root / rel
        if not path.is_file() or _signature(path) != meta["sig"]:
            changed.append(rel)
    return changed


def query(graph, terms, limit=5):
    wanted = list(dict.fromkeys(words(" ".join(terms), 2)))
    scored = []
    for entry in graph["entries"]:
        title_words = set(words(entry["title"], 2))
        path_words = set(words(entry["file"].replace("/", " ").replace(".", " "), 2))
        score, hits = 0, 0
        for term in wanted:
            gained = 0
            if term in title_words:
                gained += 5
            elif entry["kind"] == "symbol" and term in entry["title"].lower():
                gained += 3
            if term in entry["terms"]:
                gained += 3
            if term in path_words:
                gained += 2
            hits += 1 if gained else 0
            score += gained
        if wanted and hits == len(wanted):
            score += 5
        if score:
            scored.append((score, entry))
    scored.sort(key=lambda item: (-item[0], item[1]["tokens"], item[1]["file"], item[1]["start"]))
    results = []
    for score, entry in scored[:limit]:
        linked_from = sorted(src for src, targets in graph["links"].items() if entry["file"] in targets)[:3]
        results.append({**{k: entry[k] for k in ("file", "kind", "title", "start", "end", "tokens")},
                        "file_tokens": graph["files"][entry["file"]]["tokens"], "score": score, "linked_from": linked_from})
    return results


def render_query(terms, results, stale):
    if not results:
        return f'No match for "{" ".join(terms)}". Try other words, or run build if files changed.'
    lines = [f'{len(results)} results for "{" ".join(terms)}":']
    for position, r in enumerate(results, 1):
        kind = "fn " if r["kind"] == "symbol" else ""
        lines.append(f"{position}. {r['file']}  {kind}{r['title']}  lines {r['start']}-{r['end']}  open ~{r['tokens']:,} tokens (whole file ~{r['file_tokens']:,})")
        if r["linked_from"]:
            lines.append(f"     linked from: {', '.join(r['linked_from'])}")
    if stale:
        lines.append(f"warning: the index is stale ({len(stale)} files changed: {', '.join(stale[:3])}); run build")
    return "\n".join(lines)


def note_show(root):
    path = note_path(root)
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def note_write(root, text):
    cap = modo.load_config(root).get("continuity_max_tokens", NOTE_MAX_TOKENS)
    cost = walk.tokens(len(text))
    if cost > cap:
        raise ValueError(f"the note has ~{cost:,} tokens and the cap is {cap:,}: keep only goal, state, next step and decisions")
    path = note_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    config = modo.load_config(root)
    relative = ".token-diet/continuity.md"
    if relative not in config["always_loaded"]:
        config["always_loaded"].append(relative)
        modo.save_config(root, config)
    return cost


def main(argv, stdin=None):
    parser = argparse.ArgumentParser(description="Index and concept map of a project.")
    parser.add_argument("--version", action="version", version=version.label())
    parser.add_argument("command", choices=["build", "query", "note"])
    parser.add_argument("rest", nargs="*")
    parser.add_argument("--root")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--text")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    root = pathlib.Path(args.root).resolve() if args.root else modo.project_root()
    if args.command == "build":
        result = build(root, args.rest or None)
        print(f"indexed {result['entries']} entries in {result['files']} files ({result['reused']} unchanged) -> {index_dir(root) / 'index.md'}")
        return 0
    if args.command == "query":
        graph = load(root)
        if graph is None or not args.rest:
            print("error: no index yet (run build) or no terms given", file=sys.stderr)
            return 1
        print(render_query(args.rest, query(graph, args.rest, args.limit), stale_files(root, graph)))
        return 0
    action = args.rest[0] if args.rest else ""
    if action == "show":
        text = note_show(root)
        if text or not args.quiet:
            print(text if text else "No continuity note yet.")
        return 0
    if action == "write":
        text = args.text if args.text is not None else (stdin or sys.stdin).read()
        try:
            cost = note_write(root, text)
        except ValueError as error:
            print(f"error: {error}", file=sys.stderr)
            return 1
        print(f"note saved (~{cost:,} tokens)")
        return 0
    print("error: note needs show or write", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
