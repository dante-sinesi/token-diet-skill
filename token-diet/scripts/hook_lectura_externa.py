"""PreToolUse hook: forces converting before reading heavy external files.

Blocks a Read of a PDF, Office document, an image larger than 1024 px, or a big
lockfile or generated file (minified, source map) and gives the exact command that
produces something cheap to read. Small images, text and already converted files pass.

Register it in .claude/settings.json (or ~/.claude/settings.json):
  {"hooks": {"PreToolUse": [{"matcher": "Read", "hooks": [
    {"type": "command", "command": "python /path/to/hook_lectura_externa.py"}]}]}}

A broken hook never blocks work: it allows the read, writes the error to
.token-diet/hook-errors.log and, with TOKEN_DIET_HOOK_DEPURAR=1, shows it on stderr.
"""
import importlib.util
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import modo  # noqa: E402
import version  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
DOC_EXTS = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".odt", ".ods", ".odp", ".epub"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
LOCKFILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "composer.lock", "poetry.lock", "Cargo.lock", "Gemfile.lock"}
GENERATED_SUFFIXES = (".min.js", ".min.css", ".map")
GENERATED_MIN_BYTES = 20_000
MAX_IMAGE_PX = 1024
FALLBACK_IMAGE_BYTES = 200_000


def _is_generated(path):
    return path.name in LOCKFILES or path.name.endswith(GENERATED_SUFFIXES)


def _has(module):
    return importlib.util.find_spec(module) is not None


def _convert_command(path):
    return f'python "{HERE / "convertir_fuentes.py"}" "{path}"'


def _install_note(module, install):
    return "" if _has(module) else f' First install the missing library: {install}'


def _image_is_heavy(path):
    if _has("PIL"):
        from PIL import Image

        try:
            with Image.open(path) as image:
                return max(image.size) > MAX_IMAGE_PX
        except Exception:  # noqa: BLE001 - unreadable header: treat as heavy, the converter reports it
            return True
    return path.stat().st_size > FALLBACK_IMAGE_BYTES


def decide(payload, root):
    """Returns the blocking message, or None to let the read through."""
    if payload.get("tool_name") != "Read":
        return None
    raw = (payload.get("tool_input") or {}).get("file_path")
    if not raw:
        return None
    path = pathlib.Path(raw)
    if not path.is_absolute():
        path = pathlib.Path(payload.get("cwd") or root) / path
    path = path.resolve()
    suffix = path.suffix.lower()
    generated = _is_generated(path)
    if suffix not in DOC_EXTS and suffix not in IMAGE_EXTS and not generated:
        return None
    if modo.direct_read_allowed(root, path):
        return None
    sources = modo.sources_dir(root)
    if sources == path or sources in path.parents:
        return None
    if generated and (not path.is_file() or path.stat().st_size <= GENERATED_MIN_BYTES):
        return None
    if not generated and suffix in IMAGE_EXTS and (not path.is_file() or not _image_is_heavy(path)):
        return None
    count = modo.register_block(root, str(path))
    escape = f'python "{HERE / "modo.py"}" allow "{path}"'
    if generated:
        reason = f"{path.name} is a lockfile or generated file: reading it directly costs thousands of tokens for little information."
        alternative = f'python "{HERE / "compactar.py"}" "{path}", then read the summary it prints (grep the original for one package).'
    elif suffix in DOC_EXTS:
        reason = f"{path.name} is a binary document: reading it directly costs many tokens."
        note = _install_note("markitdown", 'pip install "markitdown[all]"')
        alternative = f"{_convert_command(path)}, then read the .md it prints.{note}"
    else:
        reason = f"{path.name} is larger than {MAX_IMAGE_PX} px: it costs more tokens than needed."
        note = _install_note("PIL", "pip install Pillow")
        alternative = f"{_convert_command(path)}, then read the reduced image it prints (add --max-px N for more detail).{note}"
    return modo.build_message(reason, alternative, count, escape)


def run(stdin_text, stdout, stderr, root=None):
    """Hook entry point; returns the exit code."""
    fallback = root or modo.project_root()
    try:
        payload = json.loads(stdin_text or "{}")
        message = decide(payload, root or modo.project_root(payload.get("cwd")))
    except Exception:  # noqa: BLE001 - a broken hook must not stop the work
        modo.log_error(fallback, "hook_lectura_externa")
        if modo.debug_enabled():
            import traceback

            stderr.write(traceback.format_exc())
            return 1
        return 0
    if message:
        stdout.write(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": message,
        }}))
    return 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--version"]:
        print(version.label())
        sys.exit(0)
    sys.exit(run(sys.stdin.read(), sys.stdout, sys.stderr))
