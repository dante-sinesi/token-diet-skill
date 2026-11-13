"""Compacts JSON, tables, logs, lockfiles and generated files before Claude reads them.

Usage:
  python compactar.py FILE [--mode auto|json|table|schema|log|lock|generated]
                      [--sample N] [--context N] [--out DIR] [--stdout]
  python compactar.py FILE --lines A-B     print those lines of the original

Modes (auto picks one from the file):
  json       compact JSON (no indentation), or a table when it is a list of uniform rows.
             Lossless except that a table does not show the type of scalar values.
  table      force the table form (fails if the rows are not uniform).
  schema     structure + the first --sample rows (default 5) of large JSON or CSV.
             Lossy: omitted rows are counted and the way to ask for them is printed.
  log        WARN and ERROR lines with --context lines around them (default 2), stack
             traces kept, repeats collapsed. Lossy: --lines A-B reads the original.
  lock       summary of a lockfile (package count and the first --sample packages).
  generated  summary of a minified file or source map.

Output goes to --out (default .token-diet/compact) and the report says the tokens before
and after (characters / 4). The original is never touched.
Exit codes: 0 ok, 1 error.
"""
import argparse
import csv
import hashlib
import io
import json
import math
import pathlib
import re
import sys

import guard
import modo
import terminal
import version

DEFAULT_SAMPLE = 5
DEFAULT_CONTEXT = 2
LARGE_CSV_ROWS = 200
MIN_TABLE_ROWS = 3
LOCKFILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "composer.lock", "poetry.lock", "Cargo.lock", "Gemfile.lock"}
LEVEL = re.compile(r"\b(ERROR|WARN(?:ING)?|FATAL|CRITICAL|SEVERE)\b")
TRACE_START = re.compile(r"^\s*(Traceback \(most recent call last\)|Exception in thread|Caused by:)")


class CompactError(Exception):
    pass


class Result:
    def __init__(self, text, lossy="", mode=""):
        self.text, self.lossy, self.mode = text, lossy, mode


def tokens(text):
    return math.ceil(len(text) / 4)


def _cell(value):
    if isinstance(value, (dict, list)):
        text = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
    elif value is None:
        text = "null"
    elif isinstance(value, bool):
        text = "true" if value else "false"
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def _uniform_rows(data):
    if not (isinstance(data, list) and len(data) >= MIN_TABLE_ROWS and all(isinstance(r, dict) for r in data)):
        return None
    keys = list(data[0])
    if not keys or any(list(r) != keys for r in data):
        return None
    return keys


def to_table(data, keys):
    lines = ["| " + " | ".join(keys) + " |", "|" + "---|" * len(keys)]
    lines += ["| " + " | ".join(_cell(row[k]) for k in keys) + " |" for row in data]
    return "\n".join(lines)


def compact_json(text, mode="auto"):
    try:
        data = json.loads(text)
    except ValueError as error:
        raise CompactError(f"invalid JSON: {error}") from None
    keys = _uniform_rows(data)
    if mode == "table" and keys is None:
        raise CompactError("the JSON is not a list of rows with the same keys, so it cannot be a table")
    if keys is not None and mode in ("auto", "table"):
        return Result(to_table(data, keys), "types of scalar values are not shown (a table cell has no quotes)", "table")
    return Result(json.dumps(data, separators=(",", ":"), ensure_ascii=False), "", "json")


def _type_of(values):
    names = sorted({type(v).__name__ for v in values})
    return "/".join(names)


def schema(text, suffix, sample):
    if suffix in (".csv", ".tsv"):
        reader = csv.reader(io.StringIO(text), delimiter="\t" if suffix == ".tsv" else ",")
        rows = list(reader)
        if not rows:
            raise CompactError("empty file")
        header, body = rows[0], rows[1:]
        columns = [{"name": name, "empty": sum(1 for r in body if index >= len(r) or r[index] == "")} for index, name in enumerate(header)]
        shown = [dict(zip(header, r)) for r in body[:sample]]
        total = len(body)
    else:
        try:
            data = json.loads(text)
        except ValueError as error:
            raise CompactError(f"invalid JSON: {error}") from None
        if not isinstance(data, list):
            raise CompactError("schema mode needs a list of rows (JSON array or CSV)")
        total, shown = len(data), data[:sample]
        keys = list(dict.fromkeys(k for r in data if isinstance(r, dict) for k in r))
        columns = [{"name": k, "type": _type_of([r.get(k) for r in data if isinstance(r, dict)])} for k in keys]
    out = [f"rows: {total}", "columns: " + ", ".join(
        c["name"] + (f" ({c['type']})" if "type" in c else f" ({c['empty']} empty)") for c in columns)]
    out.append(f"first {len(shown)} rows:")
    out += [json.dumps(r, separators=(",", ":"), ensure_ascii=False) for r in shown]
    omitted = max(0, total - len(shown))
    lossy = f"{omitted} rows omitted; use --mode table (JSON) or read the original by ranges to see them" if omitted else ""
    return Result("\n".join(out), lossy, "schema")


def _log_key(line):
    return re.sub(r"\d+", "#", line.strip())[:200]


def filter_log(text, context):
    lines = [terminal.clean_line(line) for line in terminal.lines_of(text)]
    keep, levels = set(), {}
    for index, line in enumerate(lines):
        match = LEVEL.search(line)
        important = terminal.is_important(line)
        if not match and not important and not TRACE_START.match(line):
            continue
        if match:
            levels[match.group(1)] = levels.get(match.group(1), 0) + 1
        elif important:
            levels["signal"] = levels.get("signal", 0) + 1
        lo, hi = max(0, index - context), min(len(lines) - 1, index + context)
        while hi + 1 < len(lines) and (lines[hi + 1][:1] in (" ", "	") or TRACE_START.match(lines[hi + 1])):
            hi += 1
        keep.update(range(lo, hi + 1))
    header = f"{len(lines)} lines; " + (
        ", ".join(f"{k} {v}" for k, v in sorted(levels.items())) if levels else "no WARN or ERROR lines")
    if not keep:
        tail = lines[-20:]
        body = [f"(showing the last {len(tail)} lines)"] + tail
        return Result("\n".join([header] + body), "no WARN or ERROR found; only the tail is shown, read by ranges with --lines", "log")
    out, previous, run, last_index = [header], None, 0, None
    for number in sorted(keep):
        line = lines[number]
        if last_index is not None and number != last_index + 1:
            out.append("...")
        key = _log_key(line)
        if key == previous:
            run += 1
        else:
            if run:
                out[-1] += f"  [x{run + 1}]"
            out.append(f"{number + 1}: {line}")
            previous, run = key, 0
        last_index = number
    if run:
        out[-1] += f"  [x{run + 1}]"
    kept = len(keep)
    return Result("\n".join(out), f"kept {kept} of {len(lines)} lines; read the rest with --lines A-B", "log")


def summarize_lock(name, text, sample):
    packages = []
    if name == "package-lock.json":
        try:
            data = json.loads(text)
        except ValueError as error:
            raise CompactError(f"invalid JSON: {error}") from None
        for path, meta in (data.get("packages") or {}).items():
            if path:
                packages.append(f"{path.split('node_modules/')[-1]}@{meta.get('version', '?')}")
        for key, meta in (data.get("dependencies") or {}).items() if not packages else []:
            packages.append(f"{key}@{meta.get('version', '?')}")
        direct = sorted((data.get("packages", {}).get("") or {}).get("dependencies", {}))
    elif name == "composer.lock":
        try:
            data = json.loads(text)
        except ValueError as error:
            raise CompactError(f"invalid JSON: {error}") from None
        packages = [f"{p['name']}@{p.get('version', '?')}" for p in data.get("packages", []) + data.get("packages-dev", [])]
        direct = []
    elif name in ("Cargo.lock", "poetry.lock"):
        packages = [f"{m[0]}@{m[1]}" for m in re.findall(r'name = "([^"]+)"\nversion = "([^"]+)"', text)]
        direct = []
    elif name == "yarn.lock":
        packages = [m for m in re.findall(r'^"?((?:@[^@\s"]+/)?[^@\s"]+)@', text, re.M)]
        direct = []
    else:
        packages = [m.strip() for m in re.findall(r"^\s{2,4}([\w@/.\-]+(?: \([^)]*\))?)$", text, re.M)]
        direct = []
    unique = list(dict.fromkeys(packages))
    out = [f"{name}: {len(unique)} packages"]
    if direct:
        out.append("direct dependencies: " + ", ".join(direct[:sample * 4]))
    out.append(f"first {min(sample * 4, len(unique))}: " + ", ".join(unique[:sample * 4]))
    return Result("\n".join(out), f"{max(0, len(unique) - sample * 4)} packages not listed; grep the original for a name", "lock")


def summarize_generated(path, text, sample):
    name = path.name
    out = [f"{name}: {len(text):,} characters, {len(text.splitlines())} lines (generated or minified)"]
    if name.endswith(".map"):
        try:
            data = json.loads(text)
            sources = data.get("sources", [])
            out.append(f"{len(sources)} sources: " + ", ".join(sources[: sample * 4]))
        except ValueError:
            out.append("not valid JSON")
    else:
        out.append("start: " + text[:300].replace("\n", " "))
    out.append("Read the original source instead of the generated file.")
    return Result("\n".join(out), "content not shown; read the source files", "generated")


def pick_mode(path, requested):
    if requested != "auto":
        return requested
    name, suffix = path.name, path.suffix.lower()
    if name in LOCKFILES:
        return "lock"
    if name.endswith(".min.js") or name.endswith(".min.css") or suffix == ".map":
        return "generated"
    if suffix == ".json":
        return "json"
    if suffix in (".csv", ".tsv"):
        return "schema"
    if suffix in (".log", ".out"):
        return "log"
    return None


def read_raw(path):
    """File text with its line endings untouched (a lone carriage return is a progress redraw, not a line break)."""
    with open(path, encoding="utf-8", errors="replace", newline="") as handle:
        return handle.read()


def compact(path, mode="auto", sample=DEFAULT_SAMPLE, context=DEFAULT_CONTEXT):
    path = pathlib.Path(path)
    if not path.is_file():
        raise CompactError("file not found")
    try:
        guard.check_size(path)
    except ValueError as error:
        raise CompactError(str(error)) from None
    chosen = pick_mode(path, mode)
    if chosen is None:
        raise CompactError("nothing to compact for this file type (use --mode to force one)")
    text = read_raw(path)
    if chosen in ("json", "table"):
        return compact_json(text, "auto" if mode == "auto" else chosen)
    if chosen == "schema":
        suffix = path.suffix.lower()
        if mode == "auto" and suffix in (".csv", ".tsv") and text.count("\n") <= LARGE_CSV_ROWS:
            raise CompactError("small CSV: already compact, read it directly")
        return schema(text, suffix, sample)
    if chosen == "log":
        return filter_log(text, context)
    if chosen == "lock":
        return summarize_lock(path.name, text, sample)
    if chosen == "generated":
        return summarize_generated(path, text, sample)
    raise CompactError(f"unknown mode: {chosen}")


def read_lines(path, spec):
    match = re.fullmatch(r"(\d+)-(\d+)", spec)
    if not match or int(match.group(1)) < 1 or int(match.group(2)) < int(match.group(1)):
        raise CompactError("--lines needs a range like 120-180")
    start, end = int(match.group(1)), int(match.group(2))
    lines = terminal.lines_of(read_raw(path))
    return "\n".join(f"{n}: {lines[n - 1].rstrip(chr(13))}" for n in range(start, min(end, len(lines)) + 1))


def main(argv):
    parser = argparse.ArgumentParser(description="Compact a file before reading it.")
    parser.add_argument("--version", action="version", version=version.label())
    parser.add_argument("file")
    parser.add_argument("--mode", default="auto", choices=["auto", "json", "table", "schema", "log", "lock", "generated"])
    parser.add_argument("--sample", type=int, default=DEFAULT_SAMPLE)
    parser.add_argument("--context", type=int, default=DEFAULT_CONTEXT)
    parser.add_argument("--out", default=".token-diet/compact")
    parser.add_argument("--stdout", action="store_true")
    parser.add_argument("--lines")
    args = parser.parse_args(argv)
    try:
        if args.lines:
            print(read_lines(args.file, args.lines))
            return 0
        result = compact(args.file, args.mode, args.sample, args.context)
    except CompactError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    source = pathlib.Path(args.file)
    original = read_raw(source)
    before = tokens(original)
    after = tokens(result.text)
    if not guard.never_worse(original, result.text, modo.profile_value(modo.project_root(), "min_gain")):
        if args.stdout:
            print(original, end="")
        else:
            print(f"{guard.NOT_WORTH}: {source}")
        return 0
    digest = hashlib.sha256((result.mode + result.text).encode("utf-8")).hexdigest()[:8]
    if args.stdout:
        print(result.text)
    else:
        target = pathlib.Path(args.out) / f"{source.stem}-{digest}.txt"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(result.text + "\n", encoding="utf-8")
        saved = round((1 - after / before) * 100) if before else 0
        print(f"compacted ({result.mode}) {source} -> {target}  ~{before:,} -> ~{after:,} tokens ({-saved:+d}%)")
    if result.lossy:
        print(f"  warning: {result.lossy}", file=sys.stderr if args.stdout else sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
