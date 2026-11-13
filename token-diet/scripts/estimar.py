"""Estimates the token cost of reading some paths, before spending it.

Usage: python estimar.py [PATH ...] [--depth N] [--top N] [--budget TOKENS] [--json]

Text files count as characters / 4. Binary files (images, PDF, Office, archives) are not
counted: convert them first with convertir_fuentes.py. Ignored folders: .git,
node_modules, __pycache__, .token-diet and similar.

--budget TOKENS exits with 1 when the estimate is over the budget, so a plan can be
approved by stages before anything is read.
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import version  # noqa: E402
import walk  # noqa: E402


def estimate(paths, depth=1):
    by_folder, files, binary = {}, [], []
    for raw in paths:
        base = pathlib.Path(raw)
        anchor = base if base.is_dir() else base.parent
        for path in walk.iter_files(base):
            if not walk.is_text(path):
                binary.append({"path": walk.relative(path, anchor), "bytes": path.stat().st_size})
                continue
            cost = walk.tokens(len(walk.read_text(path)))
            parts = pathlib.PurePosixPath(walk.relative(path, anchor)).parts
            key = "/".join(parts[:depth]) + ("/" if len(parts) > depth else "")
            by_folder[key] = by_folder.get(key, 0) + cost
            files.append({"path": walk.relative(path, anchor), "tokens": cost})
    total = sum(f["tokens"] for f in files)
    return {
        "total_tokens": total,
        "text_files": len(files),
        "folders": sorted(({"folder": k, "tokens": v} for k, v in by_folder.items()), key=lambda x: -x["tokens"]),
        "largest_files": sorted(files, key=lambda f: -f["tokens"]),
        "binary_files": len(binary),
        "binary_bytes": sum(b["bytes"] for b in binary),
    }


def render(report, top, budget=None):
    total = report["total_tokens"]
    line = f"Total: ~{total:,} tokens in {report['text_files']} text files"
    if report["binary_files"]:
        line += f" (+{report['binary_files']} binary files, {report['binary_bytes'] / 1e6:.1f} MB, not counted: convert them first)"
    lines = [line, "By folder:"]
    for item in report["folders"][:top]:
        share = round(item["tokens"] / total * 100) if total else 0
        lines.append(f"  {item['folder']:<30} ~{item['tokens']:,} ({share}%)")
    lines.append("Largest files:")
    lines += [f"  {item['path']} ~{item['tokens']:,}" for item in report["largest_files"][:top]]
    if budget is not None:
        lines.append(f"{'OVER' if total > budget else 'Within'} the budget: ~{total:,} against {budget:,}")
    return "\n".join(lines)


def main(argv):
    parser = argparse.ArgumentParser(description="Estimate the token cost of reading some paths.")
    parser.add_argument("--version", action="version", version=version.label())
    parser.add_argument("paths", nargs="*", default=["."])
    parser.add_argument("--depth", type=int, default=1)
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--budget", type=int)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = estimate(args.paths, max(1, args.depth))
    print(json.dumps(report, indent=1) if args.json else render(report, args.top, args.budget))
    return 1 if args.budget is not None and report["total_tokens"] > args.budget else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
