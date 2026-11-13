"""Shared helpers of the Token Diet scripts: walk a project and tell text from binary.

Not a command: imported by estimar.py, relevar.py, impacto.py, contexto.py and duplicados.py.
"""
import math
import os
import pathlib

IGNORED_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".token-diet", ".venv", "venv",
    "dist", "build", "target", ".idea", ".vscode", ".mypy_cache", ".pytest_cache", ".next", "vendor",
}
BINARY_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff", ".webp", ".ico", ".pdf", ".doc", ".docx", ".xls",
    ".xlsx", ".ppt", ".pptx", ".zip", ".gz", ".tar", ".7z", ".rar", ".pyc", ".so", ".dll", ".exe", ".bin",
    ".woff", ".woff2", ".ttf", ".otf", ".mp3", ".mp4", ".mov", ".sqlite", ".db",
}
LANGUAGES = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".php": "PHP", ".rb": "Ruby", ".go": "Go", ".rs": "Rust", ".java": "Java", ".kt": "Kotlin", ".c": "C",
    ".h": "C", ".cpp": "C++", ".cs": "C#", ".swift": "Swift", ".sh": "Shell", ".sql": "SQL", ".html": "HTML",
    ".css": "CSS", ".scss": "CSS", ".md": "Markdown", ".json": "JSON", ".yml": "YAML", ".yaml": "YAML",
    ".toml": "TOML",
}
CODE_LANGUAGES = {v for v in LANGUAGES.values() if v not in {"Markdown", "JSON", "YAML", "TOML", "HTML", "CSS"}}


def tokens(chars):
    return math.ceil(chars / 4)


def iter_files(root, ignored=IGNORED_DIRS):
    """Yields every file under root (sorted), skipping ignored and hidden-tool folders."""
    root = pathlib.Path(root)
    if root.is_file():
        yield root
        return
    for folder, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in ignored)
        for name in sorted(files):
            yield pathlib.Path(folder) / name


def is_text(path):
    path = pathlib.Path(path)
    if path.suffix.lower() in BINARY_EXTS:
        return False
    try:
        with open(path, "rb") as handle:
            return b"\0" not in handle.read(2048)
    except OSError:
        return False


def read_text(path):
    try:
        return pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def language_of(path):
    return LANGUAGES.get(pathlib.Path(path).suffix.lower())


def relative(path, root):
    try:
        return pathlib.Path(path).resolve().relative_to(pathlib.Path(root).resolve()).as_posix()
    except ValueError:
        return pathlib.Path(path).as_posix()
