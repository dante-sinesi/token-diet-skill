"""Case file for a change: what it touches, who it affects and what to look at first.

Usage: python contexto.py [--staged] [--base REF [--head REF]] [--root DIR] [--json]
       python contexto.py --files FILE [FILE ...] [--root DIR]
       python contexto.py --pr NUMBER [--root DIR]

Default: the working tree against HEAD (staged, unstaged and untracked files).
--staged: only what is staged. --base REF [--head REF]: the changes of a branch since it
left REF (REF...HEAD). --files: those files as they are (symbols they define and who uses them),
no diff needed. --pr N: a GitHub Pull Request, read with the gh command (TOKEN_DIET_GH picks another
executable); it needs gh installed and logged in. It replaces reading the whole diff: read the files it points to.
"""
import argparse
import json
import os
import pathlib
import re
import shlex
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import version  # noqa: E402
import impacto  # noqa: E402
import walk  # noqa: E402

RISKY = re.compile(r"(lock|migration|\.env|dockerfile|docker-compose|\.github/workflows|\.gitlab-ci|settings|config|secret|schema)", re.I)
TEST_PATH = re.compile(r"(^|/)(tests?|__tests__|spec)(/|$)|(^|/)test_[^/]*|[^/]*(_test|\.test|\.spec)\.[^/]+$", re.I)
HUNK = re.compile(r"^@@ .* @@\s*(.*)$")
USERS_LIMIT = 6
SYMBOLS_PER_FILE = 5


def git(root, *args):
    done = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    if done.returncode != 0:
        raise RuntimeError(done.stderr.strip() or "git failed")
    return done.stdout


def _range_args(staged, base, head):
    if base:
        return [f"{base}...{head or 'HEAD'}"]
    return ["--cached"] if staged else ["HEAD"]


def collect(root, staged=False, base=None, head=None):
    args = _range_args(staged, base, head)
    status = {}
    for line in git(root, "diff", "--name-status", *args).splitlines():
        code, _, path = line.partition("\t")
        status[path.split("\t")[-1]] = code[0]
    counts = {}
    for line in git(root, "diff", "--numstat", *args).splitlines():
        added, removed, path = line.split("\t", 2)
        counts[path.split(" => ")[-1].strip("{}")] = (0 if added == "-" else int(added), 0 if removed == "-" else int(removed))
    symbols, current = {}, None
    for line in git(root, "diff", "-U0", *args).splitlines():
        if line.startswith("+++ b/"):
            current = line[6:]
        elif line.startswith("@@") and current:
            match = HUNK.match(line)
            name = impacto.defined_name(match.group(1)) if match and match.group(1) else None
            if name:
                symbols.setdefault(current, set()).add(name)
        elif line.startswith("+") and not line.startswith("+++") and current:
            name = impacto.defined_name(line[1:])
            if name:
                symbols.setdefault(current, set()).add(name)
    if not base and not staged:
        for path in git(root, "ls-files", "--others", "--exclude-standard").splitlines():
            full = pathlib.Path(root) / path
            if walk.is_text(full):
                status[path] = "A"
                text = walk.read_text(full)
                counts[path] = (text.count("\n") + 1, 0)
                for line in text.splitlines():
                    name = impacto.defined_name(line)
                    if name:
                        symbols.setdefault(path, set()).add(name)
    return status, counts, symbols


def parse_patch(text):
    """Status, counts and defined symbols from a unified diff (the patch of a Pull Request)."""
    status, counts, symbols, current, in_hunk = {}, {}, {}, None, False
    for line in text.splitlines():
        if line.startswith("diff --git "):
            match = re.match(r"diff --git a/(.+) b/(.+)$", line)
            current, in_hunk = (match.group(2) if match else None), False
            if current:
                status.setdefault(current, "M")
                counts.setdefault(current, [0, 0])
        elif not current:
            continue
        elif not in_hunk and line.startswith("new file mode"):
            status[current] = "A"
        elif not in_hunk and line.startswith("deleted file mode"):
            status[current] = "D"
        elif not in_hunk and line.startswith("rename to "):
            status[current] = "R"
        elif line.startswith("@@"):
            in_hunk = True
            match = HUNK.match(line)
            name = impacto.defined_name(match.group(1)) if match and match.group(1) else None
            if name:
                symbols.setdefault(current, set()).add(name)
        elif in_hunk and line.startswith("+"):
            counts[current][0] += 1
            name = impacto.defined_name(line[1:])
            if name:
                symbols.setdefault(current, set()).add(name)
        elif in_hunk and line.startswith("-"):
            counts[current][1] += 1
    return status, {k: tuple(v) for k, v in counts.items()}, symbols


def collect_files(root, files):
    """Files as they are: every line counts as added, the symbols are the definitions they contain."""
    status, counts, symbols = {}, {}, {}
    for name in files:
        path = pathlib.Path(root) / name
        if not path.is_file():
            raise RuntimeError(f"{name} is not a file under {root}")
        text = walk.read_text(path)
        rel = walk.relative(path, root)
        status[rel], counts[rel] = "F", (len(text.splitlines()), 0)
        for line in text.splitlines():
            found = impacto.defined_name(line)
            if found:
                symbols.setdefault(rel, set()).add(found)
    return status, counts, symbols


def collect_pr(root, number):
    command = shlex.split(os.environ.get("TOKEN_DIET_GH", "gh"), posix=(os.name != "nt"))
    try:
        done = subprocess.run([*[c.strip(chr(34)) for c in command], "pr", "diff", str(number), "--patch"], cwd=root,
                              capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    except FileNotFoundError:
        raise RuntimeError("gh is not installed or not on the PATH: install it and log in, or use --base and --head") from None
    except subprocess.TimeoutExpired:
        raise RuntimeError("gh did not answer in time") from None
    if done.returncode != 0:
        raise RuntimeError("gh could not read the Pull Request: " + (done.stderr.strip().splitlines() or ["no output"])[-1][:200])
    if not done.stdout.strip():
        raise RuntimeError(f"Pull Request {number} has no diff")
    return parse_patch(done.stdout)


def build(root, staged=False, base=None, head=None, files_arg=None, pr=None):
    root = pathlib.Path(root)
    if files_arg:
        status, counts, symbols = collect_files(root, files_arg)
        mode = "files"
    elif pr:
        status, counts, symbols = collect_pr(root, pr)
        mode = "pull request"
    else:
        status, counts, symbols = collect(root, staged, base, head)
        mode = "changes"
    files = []
    for path, code in sorted(status.items()):
        added, removed = counts.get(path, (0, 0))
        files.append({"path": path, "status": code, "added": added, "removed": removed,
                      "symbols": sorted(symbols.get(path, []))[:SYMBOLS_PER_FILE], "risky": bool(RISKY.search(path)),
                      "is_test": bool(TEST_PATH.search(path))})
    changed = {f["path"] for f in files}
    for item in files:
        item["used_by"] = {}
        for name in item["symbols"]:
            if len(name) < 3:
                continue
            report = impacto.analyze(root, name, max_files=USERS_LIMIT + len(changed))
            users = [u["file"] for u in report["usage"] if u["file"] != item["path"]]
            if users:
                item["used_by"][name] = users[:USERS_LIMIT]
    def score(f):
        return f["added"] + f["removed"] + (200 if f["risky"] else 0) + 30 * len(f["used_by"])
    ranked = sorted((f for f in files if not f["is_test"]), key=score, reverse=True)
    sources = [f for f in files if not f["is_test"] and walk.language_of(f["path"]) in walk.CODE_LANGUAGES]
    warnings = []
    if mode != "files" and sources and not any(f["is_test"] for f in files):
        warnings.append("source files changed but no test file changed")
    for f in files:
        if f["status"] == "D":
            warnings.append(f"{f['path']} was deleted: check who still uses it")
    return {
        "mode": mode,
        "files_changed": len(files),
        "added": sum(f["added"] for f in files),
        "removed": sum(f["removed"] for f in files),
        "files": files,
        "look_first": [f["path"] for f in ranked[:3]],
        "warnings": warnings,
    }


def render(report):
    if not report["files"]:
        return "No changes." if report.get("mode") != "files" else "No files."
    if report.get("mode") == "files":
        lines = [f"{report['files_changed']} files as they are, {report['added']} lines"]
    elif report.get("mode") == "pull request":
        lines = [f"Pull Request: {report['files_changed']} files changed, +{report['added']} -{report['removed']}"]
    else:
        lines = [f"{report['files_changed']} files changed, +{report['added']} -{report['removed']}"]
    for f in report["files"]:
        extra = f"  symbols: {', '.join(f['symbols'])}" if f["symbols"] else ""
        flags = " [risky]" if f["risky"] else ""
        lines.append(f"  {f['status']} {f['path']} +{f['added']} -{f['removed']}{flags}{extra}")
    users = [(f["path"], n, u) for f in report["files"] for n, u in f["used_by"].items()]
    if users:
        lines.append("Used by (outside the changed file):")
        lines += [f"  {n} ({p}) -> {', '.join(u)}" for p, n, u in users[:10]]
    if report["look_first"]:
        lines.append("Look first: " + ", ".join(report["look_first"]))
    lines += [f"Warning: {w}" for w in report["warnings"]]
    return "\n".join(lines)


def main(argv):
    parser = argparse.ArgumentParser(description="Case file for a change.")
    parser.add_argument("--version", action="version", version=version.label())
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--base")
    parser.add_argument("--head")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--files", nargs="+", metavar="FILE", help="those files as they are, no diff")
    parser.add_argument("--pr", type=int, help="a GitHub Pull Request number (needs gh)")
    args = parser.parse_args(argv)
    try:
        report = build(args.root, args.staged, args.base, args.head, args.files, args.pr)
    except (RuntimeError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=1) if args.json else render(report))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
