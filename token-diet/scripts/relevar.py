"""Inventory of a system before reading it, so reading goes where it matters.

Usage: python relevar.py [ROOT] [--top N] [--out FILE] [--json]

Reports: languages (files, lines, tokens), top-level folders by weight, entry points and
manifests, test folders, the heaviest files and the git state. Output is a few dozen lines.
--out FILE also writes the report to FILE.
"""
import argparse
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import version  # noqa: E402
import walk  # noqa: E402

ENTRY_POINTS = {"main.py", "app.py", "manage.py", "__main__.py", "index.js", "index.ts", "server.js", "main.go", "main.rs", "index.php", "Program.cs"}
MANIFESTS = {"package.json", "pyproject.toml", "requirements.txt", "setup.py", "composer.json", "Cargo.toml", "go.mod", "Gemfile", "pom.xml", "build.gradle", "Makefile", "Dockerfile", "docker-compose.yml"}
TEST_MARKERS = ("test", "tests", "spec", "__tests__")


def _git(root, *args):
    try:
        done = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return done.stdout.strip() if done.returncode == 0 else None


def survey(root, top=8):
    root = pathlib.Path(root).resolve()
    languages, folders, files, entries, manifests, tests = {}, {}, [], [], [], set()
    for path in walk.iter_files(root):
        if not walk.is_text(path):
            continue
        rel = walk.relative(path, root)
        text = walk.read_text(path)
        cost, lines = walk.tokens(len(text)), text.count("\n") + 1
        language = walk.language_of(path) or "Other"
        entry = languages.setdefault(language, {"files": 0, "lines": 0, "tokens": 0})
        entry["files"] += 1
        entry["lines"] += lines
        entry["tokens"] += cost
        parts = pathlib.PurePosixPath(rel).parts
        top_level = parts[0] + "/" if len(parts) > 1 else "(root files)"
        folders[top_level] = folders.get(top_level, 0) + cost
        files.append({"path": rel, "tokens": cost})
        if path.name in ENTRY_POINTS:
            entries.append(rel)
        if path.name in MANIFESTS:
            manifests.append(rel)
        for part in parts[:-1]:
            if part.lower() in TEST_MARKERS:
                tests.add("/".join(parts[: parts.index(part) + 1]))
    git = None
    if _git(root, "rev-parse", "--git-dir") is not None:
        git = {
            "commits": _git(root, "rev-list", "--count", "HEAD"),
            "last_commit": _git(root, "log", "-1", "--format=%cs %s"),
            "branch": _git(root, "rev-parse", "--abbrev-ref", "HEAD"),
            "uncommitted_files": len((_git(root, "status", "--porcelain") or "").splitlines()),
        }
    return {
        "root": root.name,
        "total_tokens": sum(f["tokens"] for f in files),
        "files": len(files),
        "languages": sorted(({"language": k, **v} for k, v in languages.items()), key=lambda x: -x["tokens"]),
        "folders": sorted(({"folder": k, "tokens": v} for k, v in folders.items()), key=lambda x: -x["tokens"])[:top],
        "entry_points": entries[:top],
        "manifests": manifests[:top],
        "test_folders": sorted(tests)[:top],
        "heaviest_files": sorted(files, key=lambda f: -f["tokens"])[:top],
        "git": git,
    }


def render(report):
    lines = [f"{report['root']}: {report['files']} text files, ~{report['total_tokens']:,} tokens to read everything"]
    lines.append("Languages: " + ", ".join(f"{l['language']} {l['files']} files/{l['lines']:,} lines" for l in report["languages"][:6]))
    lines.append("Folders by weight: " + ", ".join(f"{f['folder']} ~{f['tokens']:,}" for f in report["folders"]))
    if report["entry_points"]:
        lines.append("Entry points: " + ", ".join(report["entry_points"]))
    if report["manifests"]:
        lines.append("Manifests: " + ", ".join(report["manifests"]))
    lines.append("Tests: " + (", ".join(report["test_folders"]) if report["test_folders"] else "no test folder found"))
    lines.append("Heaviest files: " + ", ".join(f"{f['path']} ~{f['tokens']:,}" for f in report["heaviest_files"][:5]))
    if report["git"]:
        g = report["git"]
        lines.append(f"Git: {g['commits']} commits on {g['branch']}, last: {g['last_commit']}, {g['uncommitted_files']} uncommitted files")
    else:
        lines.append("Git: not a repository")
    return "\n".join(lines)


def main(argv):
    parser = argparse.ArgumentParser(description="Inventory of a system before reading it.")
    parser.add_argument("--version", action="version", version=version.label())
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--top", type=int, default=8)
    parser.add_argument("--out")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = survey(args.root, args.top)
    output = json.dumps(report, indent=1) if args.json else render(report)
    print(output)
    if args.out:
        path = pathlib.Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
