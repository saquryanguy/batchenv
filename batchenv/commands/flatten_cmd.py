"""CLI command: flatten multiple .env files into one namespaced file."""
from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List

from batchenv.flattener import flatten_envs, format_flatten_report
from batchenv.parser import serialize_env


def run(args: Namespace) -> int:
    paths: List[Path] = [Path(p) for p in args.files]

    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        for m in missing:
            print(f"error: file not found: {m}", file=sys.stderr)
        return 1

    result = flatten_envs(
        paths,
        prefix=args.prefix if args.prefix else None,
        separator=args.separator,
        overwrite=args.overwrite,
    )

    if args.dry_run:
        print(format_flatten_report(result))
        for key, value in result.env.items():
            print(f"{key}={value}")
        return 0

    if args.output:
        out_path = Path(args.output)
        if not args.dry_run:
            out_path.write_text(serialize_env(result.env))
            print(format_flatten_report(result))
    else:
        sys.stdout.write(serialize_env(result.env))

    return 0


def register(sub: ArgumentParser) -> None:  # pragma: no cover
    sub.add_argument("files", nargs="+", help=".env files to flatten")
    sub.add_argument("--prefix", default="", help="static prefix for all keys")
    sub.add_argument(
        "--separator", default="__", help="separator between prefix and key (default: __)" 
    )
    sub.add_argument(
        "--overwrite", action="store_true", help="later files overwrite earlier values"
    )
    sub.add_argument(
        "--output", "-o", default="", help="write result to this file (default: stdout)"
    )
    sub.add_argument(
        "--dry-run", action="store_true", help="preview without writing"
    )
    sub.set_defaults(func=run)
