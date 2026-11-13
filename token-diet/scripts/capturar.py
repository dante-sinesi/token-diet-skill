"""Headless screenshot of a page or a local file, already reduced so it does not come in heavy.

Usage: python capturar.py URL_OR_FILE [--out DIR] [--max-px N] [--width W] [--height H] [--json]

Uses a browser already installed on the machine (Edge, Chrome, Chromium) in headless mode, or the
command in TOKEN_DIET_BROWSER. The raw capture is kept under <out>/raw and never needs reading; the
reduced image (long side --max-px, default 1024, never enlarged) is what you read.

Exit codes: 0 ok, 1 capture failed, 2 no browser found or Pillow missing.
"""
import argparse
import hashlib
import json
import os
import pathlib
import re
import shlex
import shutil
import subprocess
import sys

import convertir_fuentes as cf
import modo
import version

DEFAULT_OUT = ".token-diet/capture"
CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]
NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "msedge", "chrome")
INSTALL_HINT = "install Edge, Chrome or Chromium, or set TOKEN_DIET_BROWSER to the command that starts one"


class NoBrowser(Exception):
    pass


def browser_command():
    custom = os.environ.get("TOKEN_DIET_BROWSER", "").strip()
    if custom:
        parts = shlex.split(custom, posix=(os.name != "nt"))
        return [p.strip('"') for p in parts]
    for path in CANDIDATES:
        if pathlib.Path(path).is_file():
            return [path]
    for name in NAMES:
        found = shutil.which(name)
        if found:
            return [found]
    raise NoBrowser(INSTALL_HINT)


def target_uri(target):
    path = pathlib.Path(target)
    if path.is_file():
        return path.resolve().as_uri()
    if re.match(r"^(https?|file)://", target):
        return target
    raise ValueError(f"{target} is not an existing file or an http(s) or file URL")


def capture(target, out_dir, max_px=cf.DEFAULT_MAX_PX, width=1280, height=800, timeout=60):
    """Returns the conversion Result of the reduced image."""
    uri = target_uri(target)
    command = browser_command()
    out_dir = pathlib.Path(out_dir)
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^A-Za-z0-9]+", "-", uri.split("://", 1)[-1])[:40].strip("-") or "page"
    raw = raw_dir / f"{slug}-{hashlib.sha256(uri.encode()).hexdigest()[:8]}.png"
    raw.unlink(missing_ok=True)
    done = subprocess.run([*command, "--headless", "--disable-gpu", "--hide-scrollbars", f"--screenshot={raw}",
                           f"--window-size={width},{height}", uri], capture_output=True, timeout=timeout)
    if not raw.is_file() or raw.stat().st_size == 0:
        detail = (done.stderr or b"").decode("utf-8", errors="replace").strip().splitlines()[-1:] or ["no output"]
        raise RuntimeError(f"the browser did not write a screenshot ({detail[0][:120]})")
    return cf.convert(raw, out_dir, max_px)


def main(argv):
    parser = argparse.ArgumentParser(description="Headless screenshot reduced to 1024 px.")
    parser.add_argument("--version", action="version", version=version.label())
    parser.add_argument("target")
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--max-px", type=int, default=modo.profile_value(modo.project_root(), "image_px"))
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=800)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = capture(args.target, args.out, args.max_px, args.width, args.height)
    except NoBrowser as error:
        print(f"error: no browser found: {error}", file=sys.stderr)
        return 2
    except cf.MissingLibrary as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except (ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(json.dumps(cf.dataclasses.asdict(result), ensure_ascii=False) if args.json else cf.describe(result))
    return 1 if result.status == "error" else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
