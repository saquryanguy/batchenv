"""CLI command: filter — keep only matching keys/values in .env files."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from batchenv.filterer import filter_envs, format_filter_report
from batchenv.parser import serialize_env


def run(args: argparse.Namespace) -> int:
    paths = [Path(p) for p in args.files]

    missing = [p for p in paths if not p.exists()]
    if missing:
        for m in missing:
            print(f"error: file not found: {m}", file=sys.stderr)
        return 1

    if not args.key_pattern and not args.value_pattern:
        print("error: at least one of --key or --value must be specified", file=sys.stderr)
        return 1

    results = filter_envs(
        paths,
        key_pattern=args.key_pattern,
        value_pattern=args.value_pattern,
        invert=args.invert,
    )

    if args.dry_run:
        print(format_filter_report(results))
        return 0

    for result in results:
        if result.changed:
            result.path.write_text(serialize_env(result.filtered))

    print(format_filter_report(results))
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "filter",
        help="Keep only .env entries matching a key or value pattern.",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help=".env files to filter")
    p.add_argument(
        "--key",
        dest="key_pattern",
        default=None,
        metavar="REGEX",
        help="Regex pattern matched against keys (keep matching).",
    )
    p.add_argument(
        "--value",
        dest="value_pattern",
        default=None,
        metavar="REGEX",
        help="Regex pattern matched against values (keep matching).",
    )
    p.add_argument(
        "--invert",
        action="store_true",
        default=False,
        help="Invert the match — remove matching entries instead.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print what would change without modifying files.",
    )
    p.set_defaults(func=run)
