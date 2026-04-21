"""CLI command: group keys in .env files by prefix."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from batchenv.parser import parse_env_file
from batchenv.grouper import group_env, format_group_report


def run(args: argparse.Namespace) -> int:
    """Entry point for the `group` sub-command."""
    paths: List[Path] = [Path(p) for p in args.files]
    separator: str = args.separator
    min_group_size: int = args.min_group_size
    has_error = False

    for path in paths:
        if not path.exists():
            print(f"error: {path} does not exist", file=sys.stderr)
            has_error = True
            continue

        try:
            env = parse_env_file(path)
        except Exception as exc:  # noqa: BLE001
            print(f"error: could not parse {path}: {exc}", file=sys.stderr)
            has_error = True
            continue

        result = group_env(env, separator=separator, min_group_size=min_group_size)
        print(format_group_report(str(path), result))

        if args.summary:
            total_groups = len(result.groups)
            total_ungrouped = len(result.ungrouped)
            print(
                f"  summary: {total_groups} group(s), "
                f"{total_ungrouped} ungrouped key(s)"
            )

    return 1 if has_error else 0


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "group",
        help="Group .env keys by prefix and display logical sections.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="One or more .env files to analyse.",
    )
    parser.add_argument(
        "--separator",
        default="_",
        metavar="SEP",
        help="Key separator used to detect prefixes (default: '_').",
    )
    parser.add_argument(
        "--min-group-size",
        type=int,
        default=2,
        dest="min_group_size",
        metavar="N",
        help="Minimum number of keys required to form a group (default: 2).",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a summary line after each file.",
    )
    parser.set_defaults(func=run)
