"""Installs Token Diet as a Claude Code skill and registers its hooks.

Usage:
  python instalar.py install [--home DIR] [--no-note-hook]
  python instalar.py check [--home DIR]
  python instalar.py uninstall [--home DIR]

install    copies token-diet/ to <home>/.claude/skills/token-diet/, writes a manifest
           (where it came from and a hash of every file) and registers two hooks in
           <home>/.claude/settings.json:
             PreToolUse (Read)  hook_lectura_externa.py  blocks heavy reads and gives the command
             SessionStart       indexar_docs.py note show --quiet  loads the continuity note
                                (skipped with --no-note-hook; prints nothing without a note)
           The settings file is backed up first to settings.json.token-diet.bak, everything
           else in it is kept, and a previous Token Diet registration is replaced, not duplicated.
           Running it again is safe. A settings file that is not valid JSON is never touched.
check      says whether the installed copy still matches the repository it came from and
           whether the hooks are registered. Exit code 1 if something drifted or is missing.
uninstall  removes the skill and its hooks (same backup rule).
"""
import argparse
import datetime
import hashlib
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent
SOURCE = ROOT / "token-diet"


def source_version():
    try:
        return (SOURCE / "VERSION").read_text(encoding="utf-8").strip()
    except OSError:
        return "unknown"


SKILL_NAME = "token-diet"
MANIFEST = ".install.json"
BACKUP = "settings.json.token-diet.bak"
HOOK_SCRIPTS = ("hook_lectura_externa.py", "indexar_docs.py")
IGNORED = {"__pycache__"}


class InstallError(Exception):
    pass


def skill_dir(home):
    return pathlib.Path(home) / ".claude" / "skills" / SKILL_NAME


def settings_path(home):
    return pathlib.Path(home) / ".claude" / "settings.json"


def file_hashes(base):
    base = pathlib.Path(base)
    hashes = {}
    for path in sorted(base.rglob("*")):
        relative = path.relative_to(base)
        if path.is_file() and not (set(relative.parts) & IGNORED) and path.suffix != ".pyc" and path.name != MANIFEST:
            hashes[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def hook_commands(home, note_hook=True):
    scripts = (skill_dir(home) / "scripts").as_posix()
    commands = {"PreToolUse": ('Read', f'python "{scripts}/hook_lectura_externa.py"')}
    if note_hook:
        commands["SessionStart"] = (None, f'python "{scripts}/indexar_docs.py" note show --quiet')
    return commands


def _is_ours(command):
    return SKILL_NAME in command and any(script in command for script in HOOK_SCRIPTS)


def load_settings(home):
    path = settings_path(home)
    if not path.is_file():
        return {}, None
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text) if text.strip() else {}
    except ValueError as error:
        raise InstallError(f"{path} is not valid JSON ({error}); it was left untouched") from None
    if not isinstance(data, dict):
        raise InstallError(f"{path} is not a JSON object; it was left untouched")
    return data, text


def remove_ours(settings):
    """Removes every Token Diet hook; returns how many were removed."""
    removed = 0
    hooks = settings.get("hooks")
    if not isinstance(hooks, dict):
        return 0
    for event in list(hooks):
        kept = []
        for entry in hooks[event]:
            inner = entry.get("hooks", []) if isinstance(entry, dict) else []
            left = [h for h in inner if not (isinstance(h, dict) and _is_ours(h.get("command", "")))]
            removed += len(inner) - len(left)
            if left or not inner:
                kept.append({**entry, "hooks": left} if inner else entry)
        if kept:
            hooks[event] = kept
        else:
            del hooks[event]
    if not hooks:
        del settings["hooks"]
    return removed


def write_settings(home, settings, original):
    path = settings_path(home)
    path.parent.mkdir(parents=True, exist_ok=True)
    new_text = json.dumps(settings, indent=2, ensure_ascii=False) + "\n"
    if original is not None and original != new_text:
        shutil.copyfile(path, path.with_name(BACKUP))
    path.write_text(new_text, encoding="utf-8")


def install(home, note_hook=True):
    if not SOURCE.is_dir():
        raise InstallError(f"{SOURCE} not found: run the installer from the repository")
    settings, original = load_settings(home)
    target = skill_dir(home)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(SOURCE, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    hooks = hook_commands(home, note_hook)
    (target / MANIFEST).write_text(json.dumps({
        "source": str(ROOT),
        "version": source_version(),
        "installed_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "files": file_hashes(target),
        "hooks": sorted(hooks),
    }, indent=1), encoding="utf-8")
    remove_ours(settings)
    registry = settings.setdefault("hooks", {})
    for event, (matcher, command) in hooks.items():
        entry = {"hooks": [{"type": "command", "command": command}]}
        if matcher:
            entry = {"matcher": matcher, **entry}
        registry.setdefault(event, []).append(entry)
    write_settings(home, settings, original)
    return {"files": len(file_hashes(target)), "hooks": sorted(hooks), "target": target}


def uninstall(home):
    settings, original = load_settings(home)
    removed = remove_ours(settings)
    if original is not None:
        write_settings(home, settings, original)
    target = skill_dir(home)
    existed = target.exists()
    if existed:
        shutil.rmtree(target)
    return {"skill_removed": existed, "hooks_removed": removed}


def check(home, note_hook=True):
    problems = []
    target = skill_dir(home)
    manifest_path = target / MANIFEST
    if not manifest_path.is_file():
        return ["not installed (no manifest found)"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    installed = file_hashes(target)
    for name, digest in manifest["files"].items():
        if name not in installed:
            problems.append(f"installed file missing: {name}")
        elif installed[name] != digest:
            problems.append(f"installed file was edited after the install: {name}")
    source = pathlib.Path(manifest["source"]) / "token-diet"
    if source.is_dir():
        origin = file_hashes(source)
        for name, digest in origin.items():
            if name not in installed:
                problems.append(f"repository has a new file that is not installed: {name}")
            elif installed[name] != digest:
                problems.append(f"repository differs from the installed copy: {name}")
        for name in installed:
            if name not in origin:
                problems.append(f"installed file no longer in the repository: {name}")
    else:
        problems.append(f"the repository it came from is no longer at {manifest['source']}")
    try:
        settings, _ = load_settings(home)
    except InstallError as error:
        return problems + [str(error)]
    registered = [
        (event, h.get("command", ""))
        for event, entries in (settings.get("hooks") or {}).items() for entry in entries for h in entry.get("hooks", [])
        if isinstance(h, dict) and _is_ours(h.get("command", ""))
    ]
    for event, (_, command) in hook_commands(home, "SessionStart" in manifest["hooks"]).items():
        if (event, command) not in registered:
            problems.append(f"hook not registered or pointing elsewhere: {event}")
    return problems


def main(argv):
    parser = argparse.ArgumentParser(description="Install Token Diet as a Claude Code skill.")
    parser.add_argument("command", choices=["install", "check", "uninstall"])
    parser.add_argument("--version", action="version", version=f"token-diet {source_version()}")
    parser.add_argument("--home", default=str(pathlib.Path.home()))
    parser.add_argument("--no-note-hook", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "install":
            result = install(args.home, not args.no_note_hook)
            print(f"installed token-diet {source_version()}: {result['files']} files in {result['target']}")
            print("hooks registered: " + ", ".join(result["hooks"]))
            return 0
        if args.command == "uninstall":
            result = uninstall(args.home)
            print(f"skill removed: {result['skill_removed']}; hooks removed: {result['hooks_removed']}")
            return 0
        problems = check(args.home)
        manifest_file = skill_dir(args.home) / MANIFEST
        installed = json.loads(manifest_file.read_text(encoding="utf-8")).get("version", "unknown") if manifest_file.is_file() else "none"
        print(f"installed version: {installed}; repository version: {source_version()}")
        print("\n".join(f"problem: {p}" for p in problems) if problems else "installed copy and hooks are in order")
        return 1 if problems else 0
    except InstallError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
