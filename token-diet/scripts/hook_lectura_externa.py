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


def _image_is_heavy(path, max_px=MAX_IMAGE_PX):
    if _has("PIL"):
        from PIL import Image

        try:
            with Image.open(path) as image:
                return max(image.size) > max_px
        except Exception:  # noqa: BLE001 - unreadable header: treat as heavy, the converter reports it
            return True
    return path.stat().st_size > FALLBACK_IMAGE_BYTES


def _lines_above(path, cap):
    """Line count of a text file when it is above `cap` (stops counting there), else 0."""
    try:
        with open(path, "rb") as handle:
            if b"\0" in handle.read(2048):
                return 0
            handle.seek(0)
            count = 0
            for count, _ in enumerate(handle, 1):
                if count > cap:
                    break
            else:
                return 0
            return sum(1 for _ in handle) + count
    except OSError:
        return 0


def _read_cap_message(payload, root, path, tool_input):
    """Soft block, once per file and session: a long file read whole gets the way to read a range."""
    if tool_input.get("offset") or tool_input.get("limit"):
        return None
    state = modo.state_dir(root)
    if state == path or state in path.parents or not path.is_file():
        return None
    cap = modo.profile_value(root, "read_cap_lines")
    lines = _lines_above(path, cap)
    if not lines:
        return None
    session = str(payload.get("session_id") or "none")
    count = modo.register_block(root, f"cap:{session}:{path}")
    if count > 1:
        return None
    tokens = max(1, path.stat().st_size // 4)
    reason = f"{path.name} has {lines:,} lines (about {tokens:,} tokens): reading all of it is rarely needed."
    alternative = (f"read a range (Read with offset 1 and limit {cap}), find the part with "
                   f'python "{HERE / "indexar_docs.py"}" query TERMS, or compact it with python "{HERE / "compactar.py"}" "{path}"')
    return modo.build_message(reason, alternative, 1, "repeat the same Read and it goes through")


def _reread_message(payload, root, path, tool_input):
    """Soft block, once: the same unchanged range of a file read again in the same session."""
    try:
        stat = path.stat()
    except OSError:
        return None
    session = str(payload.get("session_id") or "none")
    key = f"seen:{session}:{path}:{stat.st_mtime_ns}:{stat.st_size}:{tool_input.get('offset') or 0}:{tool_input.get('limit') or 0}"
    if modo.register_block(root, key) != 2:
        return None
    reason = f"{path.name} was already read in this session and has not changed: its text is in the conversation."
    alternative = "use what you read; if you need another part, read that range (offset and limit) or search the file"
    return modo.build_message(reason, alternative, 1, "repeat the same Read and it goes through")


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
    if modo.direct_read_allowed(root, path):
        return None
    if suffix not in DOC_EXTS and suffix not in IMAGE_EXTS and not generated:
        tool_input = payload.get("tool_input") or {}
        message = _read_cap_message(payload, root, path, tool_input)
        state = modo.state_dir(root)
        if message or not path.is_file() or state == path or state in path.parents:
            return message
        return _reread_message(payload, root, path, tool_input)
    sources = modo.sources_dir(root)
    if sources == path or sources in path.parents:
        return None
    max_px = modo.profile_value(root, "image_px")
    if generated and (not path.is_file() or path.stat().st_size <= modo.profile_value(root, "generated_min_bytes")):
        return None
    if not generated and suffix in IMAGE_EXTS and (not path.is_file() or not _image_is_heavy(path, max_px)):
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
        reason = f"{path.name} is larger than {max_px} px: it costs more tokens than needed."
        note = _install_note("PIL", "pip install Pillow")
        alternative = f"{_convert_command(path)}, then read the reduced image it prints (add --max-px N for more detail).{note}"
    return modo.build_message(reason, alternative, count, escape)


def run(stdin_text, stdout, stderr, root=None):
    """Hook entry point; returns the exit code."""
    fallback = root or modo.project_root()
    for problem in modo.installation_problems(HERE):
        modo.log_note(fallback, "hook_lectura_externa", f"integrity: {problem}; the hook keeps working, run instalar.py check")
        if modo.debug_enabled():
            stderr.write(f"integrity: {problem}\n")
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
