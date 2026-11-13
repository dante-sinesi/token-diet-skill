"""Converts documents to Markdown and shrinks images before Claude reads them.

Usage:
  python convertir_fuentes.py FILE_OR_DIR [...] [--out DIR] [--max-px N] [--json]

Documents (PDF, Word, Excel, PowerPoint, HTML, ...) become Markdown with
`markitdown`; read the .md, never the original. Images are reduced to
--max-px (default 1024) on the long side, never enlarged, respecting EXIF.
Plain text, JSON and CSV are left alone (no gain from converting them).

Output goes to --out (default: $TOKEN_DIET_SOURCES_DIR or .token-diet/sources),
images to <out>/images. A hash cache skips what did not change.

Exit codes: 0 ok, 1 some file failed, 2 a required library is missing.
Emergency exit: --max-px asks for a larger image; the original is never touched.
"""
import argparse
import dataclasses
import hashlib
import json
import math
import os
import pathlib
import shutil
import sys

import guard
import version

DEFAULT_MAX_PX = 1024
API_IMAGE_CAP_PX = 1568
MIN_TEXT_CHARS = 200
LONG_TEXT_CHARS = 2000

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
KEEP_FORMAT = {".png": ".png", ".jpg": ".jpg", ".jpeg": ".jpg", ".webp": ".webp"}
PASSTHROUGH_EXTS = {".md", ".txt", ".log", ".json", ".csv", ".tsv"}
RAW_TEXT_EXTS = {".html", ".htm", ".xml"}


class MissingLibrary(Exception):
    def __init__(self, name, install):
        super().__init__(f"{name} is not installed. Install it with: {install}")
        self.name = name
        self.install = install


@dataclasses.dataclass
class Result:
    source: str
    status: str  # converted | cached | passthrough | error
    output: str = ""
    tokens_before: int = None
    tokens_after: int = None
    warnings: list = dataclasses.field(default_factory=list)
    message: str = ""


def tokens_of_text(chars):
    return math.ceil(chars / 4)


def tokens_of_image(width, height):
    return math.ceil(width * height / 750)


def _capped(width, height, cap):
    longest = max(width, height)
    if longest <= cap:
        return width, height
    scale = cap / longest
    return max(1, round(width * scale)), max(1, round(height * scale))


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_pillow():
    try:
        from PIL import Image, ImageOps
    except ImportError:
        raise MissingLibrary("Pillow", "pip install Pillow") from None
    return Image, ImageOps


def _load_markitdown():
    try:
        from markitdown import MarkItDown
    except ImportError:
        raise MissingLibrary("markitdown", 'pip install "markitdown[all]"') from None
    return MarkItDown


def _cache_path(out_dir):
    return out_dir / ".cache.json"


def _read_cache(out_dir):
    try:
        return json.loads(_cache_path(out_dir).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _write_cache(out_dir, cache):
    out_dir.mkdir(parents=True, exist_ok=True)
    _cache_path(out_dir).write_text(json.dumps(cache, indent=1, sort_keys=True), encoding="utf-8")


def convert_image(src, out_dir, max_px=DEFAULT_MAX_PX):
    """Returns (output_path, tokens_before, tokens_after, warnings)."""
    Image, ImageOps = _load_pillow()
    digest = sha256_file(src)
    ext = KEEP_FORMAT.get(src.suffix.lower(), ".png")
    target = out_dir / "images" / f"{src.stem}-{digest[:8]}{ext}"
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as image:
        needs_turn = image.getexif().get(0x0112, 1) not in (0, 1)
        oriented = ImageOps.exif_transpose(image) if needs_turn else image
        width, height = oriented.size
        before = tokens_of_image(*_capped(width, height, API_IMAGE_CAP_PX))
        new_size = _capped(width, height, max_px)
        resized = new_size != (width, height)
        if not resized and not needs_turn and src.suffix.lower() in KEEP_FORMAT:
            shutil.copyfile(src, target)
        else:
            result = oriented.resize(new_size, Image.LANCZOS) if resized else oriented
            if ext == ".jpg" and result.mode != "RGB":
                result = result.convert("RGB")
            options = {"quality": 90, "optimize": True} if ext in (".jpg", ".webp") else {"optimize": True}
            result.save(target, **options)
        after = tokens_of_image(*new_size)
    return target, before, after, []


def convert_document(src, out_dir):
    markitdown = _load_markitdown()
    digest = sha256_file(src)
    text = markitdown().convert(str(src)).text_content or ""
    warnings = []
    if len(text.strip()) < MIN_TEXT_CHARS:
        warnings.append("little text extracted: the conversion may have lost information (scanned or image-only?)")
    elif len(text) > LONG_TEXT_CHARS and not any(line.lstrip().startswith("#") for line in text.splitlines()):
        warnings.append("long output without headings: the document structure may have been lost")
    target = out_dir / f"{src.stem}-{digest[:8]}.md"
    out_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    before = tokens_of_text(src.stat().st_size) if src.suffix.lower() in RAW_TEXT_EXTS else None
    return target, before, tokens_of_text(len(text)), warnings


def convert(src, out_dir, max_px=DEFAULT_MAX_PX):
    src = pathlib.Path(src)
    out_dir = pathlib.Path(out_dir)
    if not src.is_file():
        return Result(str(src), "error", message="file not found")
    suffix = src.suffix.lower()
    if suffix in PASSTHROUGH_EXTS:
        hint = " (use compaction instead: converting does not shrink it)" if suffix in {".json", ".csv", ".tsv"} else ""
        return Result(str(src), "passthrough", message=f"already text, read it directly{hint}")
    is_image = suffix in IMAGE_EXTS
    if not is_image:
        try:
            guard.check_size(src)
        except ValueError as error:
            return Result(str(src), "error", message=str(error))
    key = f"{sha256_file(src)}:{max_px if is_image else 0}"
    cache = _read_cache(out_dir)
    entry = cache.get(str(src.resolve()))
    if entry and entry["key"] == key and pathlib.Path(entry["output"]).is_file():
        return Result(str(src), "cached", entry["output"], entry["before"], entry["after"], entry["warnings"])
    try:
        if is_image:
            output, before, after, warnings = convert_image(src, out_dir, max_px)
        else:
            output, before, after, warnings = convert_document(src, out_dir)
    except MissingLibrary:
        raise
    except Exception as error:  # noqa: BLE001 - report any converter failure per file
        return Result(str(src), "error", message=f"{type(error).__name__}: {error}")
    if not is_image and before is not None and after >= before:
        pathlib.Path(output).unlink(missing_ok=True)
        return Result(str(src), "passthrough", message="the Markdown is not smaller than the original: read the original")
    cache[str(src.resolve())] = {
        "key": key, "output": str(output), "before": before, "after": after, "warnings": warnings,
    }
    _write_cache(out_dir, cache)
    return Result(str(src), "converted", str(output), before, after, warnings)


def _expand(paths):
    for raw in paths:
        path = pathlib.Path(raw)
        if path.is_dir():
            for found in sorted(path.rglob("*")):
                if found.is_file() and not any(part.startswith(".") for part in found.relative_to(path).parts):
                    yield found
        else:
            yield path


def describe(result):
    if result.status in ("passthrough", "error"):
        return f"{result.status:<11} {result.source}: {result.message}"
    line = f"{result.status:<11} {result.source} -> {result.output}"
    if result.tokens_after is not None:
        if result.tokens_before:
            saved = round((1 - result.tokens_after / result.tokens_before) * 100)
            line += f"  ~{result.tokens_before:,} -> ~{result.tokens_after:,} tokens ({-saved:+d}%)"
        else:
            line += f"  ~{result.tokens_after:,} tokens"
    return line


def main(argv):
    parser = argparse.ArgumentParser(description="Convert documents to Markdown and shrink images.")
    parser.add_argument("--version", action="version", version=version.label())
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--out", default=os.environ.get("TOKEN_DIET_SOURCES_DIR", ".token-diet/sources"))
    parser.add_argument("--max-px", type=int, default=DEFAULT_MAX_PX)
    parser.add_argument("--json", action="store_true", help="print one JSON object per file")
    args = parser.parse_args(argv)
    if args.max_px < 1:
        parser.error("--max-px must be positive")
    out_dir = pathlib.Path(args.out)
    failed = False
    for path in _expand(args.paths):
        try:
            result = convert(path, out_dir, args.max_px)
        except MissingLibrary as error:
            print(f"error: {error}", file=sys.stderr)
            return 2
        failed = failed or result.status == "error"
        if args.json:
            print(json.dumps(dataclasses.asdict(result), ensure_ascii=False))
        else:
            print(describe(result))
            for warning in result.warnings:
                print(f"  warning: {warning}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
