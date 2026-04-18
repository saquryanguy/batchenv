"""strip command — remove comments and blank lines from .env files."""
from __future__ import annotations

import argparse
from pathlib import Path

from batchenv.parser import parse_env_file, serialize_env
from batchenv.stripper import strip_envs, format_strip_report


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="batchenv strip",
        description="Remove comments and blank lines from .env files.",
    )
    parser.add_argument("files", nargs="+", help=".env files to strip")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing files.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output.",
    )
    args = parser.parse_args(argv)

    paths = [Path(f) for f in args.files]
    missing = [p for p in paths if not p.exists()]
    if missing:
        for m in missing:
            print(f"error: file not found: {m}")
        return 1

    envs = {p: parse_env_file(p) for p in paths}
    results = strip_envs(envs)

    if not args.quiet:
        print(format_strip_report(results))

    if args.dry_run:
        return 0

    for path, result in results.items():
        if result.changed:
            path.write_text(serialize_env(result.stripped))

    return 0
