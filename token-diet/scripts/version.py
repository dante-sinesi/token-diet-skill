"""Version of the installed Token Diet, read from the VERSION file next to scripts/."""
import pathlib


def read():
    try:
        return (pathlib.Path(__file__).resolve().parent.parent / "VERSION").read_text(encoding="utf-8").strip() or "unknown"
    except OSError:
        return "unknown"


def label():
    return f"token-diet {read()}"
