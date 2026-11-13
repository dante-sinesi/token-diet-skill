"""Configuration and block log shared by the Token Diet hooks.

State lives in <project>/.token-diet/config.json:
  {"direct_read": ["pattern", ...], "blocks": {"<key>": count}, "always_loaded": ["file", ...]}

Hooks only ever block with the exact alternative; they never tell anyone to wait
for the user. A repeated block is counted and, from the third time, the message
puts the alternative first.

Environment:
  TOKEN_DIET_LECTURA_DIRECTA=1  disable the read blocks (emergency exit)
  TOKEN_DIET_HOOK_DEPURAR=1     show hook errors on stderr and exit with 1

Command line:
  python modo.py allow PATTERN   let matching files be read directly
  python modo.py show            print the configuration
"""
import fnmatch
import json
import os
import pathlib
import sys
import traceback

ENV_DIRECT = "TOKEN_DIET_LECTURA_DIRECTA"
ENV_DEBUG = "TOKEN_DIET_HOOK_DEPURAR"
REPEAT_AT = 3
TRUE_VALUES = {"1", "true", "yes", "on"}


def _enabled(name):
    return os.environ.get(name, "").strip().lower() in TRUE_VALUES


def debug_enabled():
    return _enabled(ENV_DEBUG)


def project_root(cwd=None):
    return pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or cwd or os.getcwd()).resolve()


def state_dir(root):
    return pathlib.Path(root) / ".token-diet"


def sources_dir(root):
    return pathlib.Path(os.environ.get("TOKEN_DIET_SOURCES_DIR") or state_dir(root) / "sources").resolve()


def _config_path(root):
    return state_dir(root) / "config.json"


def load_config(root):
    try:
        data = json.loads(_config_path(root).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    data.setdefault("direct_read", [])
    data.setdefault("blocks", {})
    data.setdefault("always_loaded", [])
    return data


def save_config(root, config):
    path = _config_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=1, sort_keys=True), encoding="utf-8")


def direct_read_allowed(root, path):
    if _enabled(ENV_DIRECT):
        return True
    posix = pathlib.Path(path).as_posix()
    name = pathlib.Path(path).name
    return any(fnmatch.fnmatch(posix, p) or fnmatch.fnmatch(name, p) for p in load_config(root)["direct_read"])


def allow(root, pattern):
    config = load_config(root)
    if pattern not in config["direct_read"]:
        config["direct_read"].append(pattern)
        save_config(root, config)


def register_block(root, key):
    """Counts a block for `key` and returns how many times it happened."""
    config = load_config(root)
    config["blocks"][key] = config["blocks"].get(key, 0) + 1
    save_config(root, config)
    return config["blocks"][key]


def build_message(reason, alternative, count=1, escape=None):
    """Blocking message: always the exact alternative, never a request to wait."""
    lines = [f"Do this instead: {alternative}", f"Why: {reason}"]
    if count < REPEAT_AT:
        lines.reverse()
    if escape:
        lines.append(f"To read the original anyway: {escape}")
    return "\n".join(lines)


def log_error(root, hook):
    try:
        folder = state_dir(root)
        folder.mkdir(parents=True, exist_ok=True)
        with open(folder / "hook-errors.log", "a", encoding="utf-8") as handle:
            handle.write(f"[{hook}]\n{traceback.format_exc()}\n")
    except OSError:
        pass


def main(argv):
    root = project_root()
    if argv[:1] == ["allow"] and len(argv) == 2:
        allow(root, argv[1])
        print(f"allowed: {argv[1]}")
        return 0
    if argv[:1] == ["show"]:
        print(json.dumps(load_config(root), indent=1, sort_keys=True))
        return 0
    print(__doc__, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
