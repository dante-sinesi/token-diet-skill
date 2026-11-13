"""Audits what is loaded in every session and says what to trim first.

Usage: python consumo.py [--root DIR] [--home DIR] [--repo DIR] [--json] [--out FILE]

Fixed cost (paid every session): skill names and descriptions, CLAUDE.md files, the
memory index and any extra file listed in .token-diet/config.json under "always_loaded".
On activation (paid when a skill comes into play): the body of each SKILL.md.
Tokens are characters / 4, good for comparing, not exact.

Limits: description 800 characters, body 500 lines or 5,000 tokens, CLAUDE.md 2,500
tokens, memory index 200 lines, MCP servers 3.

--repo DIR audits the skills found in a repository as if they were installed (a skill
with the same name replaces the installed one), so you see the effect without installing.
--out FILE also writes the report to FILE.

Exit codes: 0 nothing over a limit, 1 something over a limit.
"""
import argparse
import json
import math
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import modo  # noqa: E402

DESC_MAX_CHARS = 800
BODY_MAX_LINES = 500
BODY_MAX_TOKENS = 5000
CLAUDE_MAX_TOKENS = 2500
MEMORY_MAX_LINES = 200
MCP_MAX = 3


def tokens(text):
    return math.ceil(len(text) / 4)


def _read(path):
    try:
        return pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def parse_skill(path):
    """Returns {name, description, body_lines, body_tokens, path} or None."""
    text = _read(path)
    if text is None:
        return None
    match = re.match(r"---\r?\n(.*?)\r?\n---\r?\n?(.*)", text, re.S)
    if not match:
        return None
    front, body = match.groups()
    fields, key = {}, None
    for line in front.splitlines():
        head = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if head:
            key = head.group(1)
            value = head.group(2).strip()
            fields[key] = "" if value in (">", ">-", "|", "|-") else value.strip("\"'")
        elif key and line.startswith((" ", "\t")):
            fields[key] = (fields[key] + " " + line.strip()).strip()
    name = fields.get("name") or pathlib.Path(path).parent.name
    return {
        "name": name,
        "description": fields.get("description", ""),
        "body_lines": len(body.splitlines()),
        "body_tokens": tokens(body),
        "path": str(path),
    }


def find_skills(base):
    skills = {}
    for path in sorted(pathlib.Path(base).glob("*/SKILL.md")):
        skill = parse_skill(path)
        if skill:
            skills[skill["name"]] = skill
    return skills


def repo_skills(repo):
    skills = {}
    for path in sorted(pathlib.Path(repo).rglob("SKILL.md")):
        if any(part.startswith(".") or part == "node_modules" for part in path.relative_to(repo).parts):
            continue
        skill = parse_skill(path)
        if skill:
            skills[skill["name"]] = skill
    return skills


def memory_index(home, root):
    slug = re.sub(r"[^A-Za-z0-9]", "-", str(root))
    return pathlib.Path(home) / ".claude" / "projects" / slug / "memory" / "MEMORY.md"


def mcp_servers(home, root):
    names = set()

    def collect(data):
        if isinstance(data, dict) and isinstance(data.get("mcpServers"), dict):
            names.update(data["mcpServers"])

    for path in (pathlib.Path(root) / ".mcp.json", pathlib.Path(home) / ".claude.json"):
        text = _read(path)
        try:
            data = json.loads(text) if text else {}
        except ValueError:
            continue
        collect(data)
        if path.name == ".claude.json":
            wanted = pathlib.Path(root).resolve()
            for key, project in (data.get("projects") or {}).items():
                try:
                    if pathlib.Path(key).resolve() == wanted:
                        collect(project)
                except OSError:
                    pass
    return sorted(names)


def _audit(root, home, repo):
    root, home = pathlib.Path(root).resolve(), pathlib.Path(home)
    skills = {}
    for base in (home / ".claude" / "skills", root / ".claude" / "skills"):
        skills.update(find_skills(base))
    if repo:
        skills.update(repo_skills(repo))
    items, problems = [], []

    def fixed(kind, label, text, **extra):
        items.append({"kind": kind, "label": label, "tokens": tokens(text), **extra})

    for skill in skills.values():
        fixed("skill", skill["name"], f'{skill["name"]}: {skill["description"]}', chars=len(skill["description"]))
        if len(skill["description"]) > DESC_MAX_CHARS:
            problems.append(f'skill {skill["name"]}: description has {len(skill["description"])} characters (limit {DESC_MAX_CHARS})')
        if skill["body_lines"] > BODY_MAX_LINES or skill["body_tokens"] > BODY_MAX_TOKENS:
            problems.append(f'skill {skill["name"]}: body has {skill["body_lines"]} lines and ~{skill["body_tokens"]:,} tokens (limits {BODY_MAX_LINES} / {BODY_MAX_TOKENS:,})')
    for path in (home / ".claude" / "CLAUDE.md", root / "CLAUDE.md", root / "CLAUDE.local.md"):
        text = _read(path)
        if text is not None:
            fixed("claude_md", str(path.name if path.parent == root else "~/.claude/CLAUDE.md"), text)
            if tokens(text) > CLAUDE_MAX_TOKENS:
                problems.append(f"{path.name}: ~{tokens(text):,} tokens (limit {CLAUDE_MAX_TOKENS:,})")
    text = _read(memory_index(home, root))
    if text is not None:
        fixed("memory", "MEMORY.md", text)
        if len(text.splitlines()) > MEMORY_MAX_LINES:
            problems.append(f"MEMORY.md: {len(text.splitlines())} lines (limit {MEMORY_MAX_LINES})")
    for relative in modo.load_config(root).get("always_loaded", []):
        text = _read(root / relative)
        if text is not None:
            fixed("always_loaded", relative, text)
    servers = mcp_servers(home, root)
    if len(servers) > MCP_MAX:
        problems.append(f"{len(servers)} MCP servers (limit {MCP_MAX}); their tool definitions are not counted here")
    total = sum(item["tokens"] for item in items)
    ranked = sorted(items, key=lambda i: i["tokens"], reverse=True)
    return {
        "fixed_tokens": total,
        "items": items,
        "mcp_servers": servers,
        "problems": problems,
        "trim_first": [{"label": i["label"], "tokens": i["tokens"]} for i in ranked[:3]],
        "skills": [{"name": s["name"], "body_tokens": s["body_tokens"], "body_lines": s["body_lines"]} for s in skills.values()],
        "repo_effect": None,
    }


def audit(root, home, repo=None):
    report = _audit(root, home, repo)
    if repo:
        report["repo_effect"] = {"fixed_tokens_added": report["fixed_tokens"] - _audit(root, home, None)["fixed_tokens"]}
    return report


def render(report):
    by_kind = {}
    for item in report["items"]:
        by_kind[item["kind"]] = by_kind.get(item["kind"], 0) + item["tokens"]
    names = {"skill": "skills", "claude_md": "CLAUDE.md", "memory": "memory index", "always_loaded": "always-loaded files"}
    parts = ", ".join(f"{names[k]} ~{v:,}" for k, v in by_kind.items())
    lines = [f"Fixed cost per session: ~{report['fixed_tokens']:,} tokens" + (f" ({parts})" if parts else "")]
    lines.append(f"MCP servers: {len(report['mcp_servers'])} (tool definitions not counted)")
    if report["repo_effect"]:
        lines.append(f"--repo: the repository skills add ~{report['repo_effect']['fixed_tokens_added']:,} fixed tokens")
    if report["problems"]:
        lines.append("Over the limit:")
        lines += [f"  - {problem}" for problem in report["problems"]]
    else:
        lines.append("Nothing over the limits.")
    if report["trim_first"]:
        lines.append("Largest fixed items: " + ", ".join(f"{t['label']} ~{t['tokens']:,}" for t in report["trim_first"]))
    return "\n".join(lines)


def main(argv):
    parser = argparse.ArgumentParser(description="Audit what is loaded in every session.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--home", default=str(pathlib.Path.home()))
    parser.add_argument("--repo")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    report = audit(args.root, args.home, args.repo)
    output = json.dumps(report, indent=1) if args.json else render(report)
    print(output)
    if args.out:
        path = pathlib.Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output + "\n", encoding="utf-8")
    return 1 if report["problems"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
