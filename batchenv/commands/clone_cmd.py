"""CLI command: clone an env file to one or more destinations."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from batchenv.cloner import clone_env, format_clone_report


def run(args: argparse.Namespace) -> int:
    """Entry point for the ``clone`` sub-command.

    Returns 0 on success, 1 if any error occurs.
    """
    source = Path(args.source)
    if not source.exists():
        print(f"error: source file not found: {source}")
        return 1

    destinations: List[Path] = [Path(d) for d in args.destinations]
    if not destinations:
        print("error: at least one destination must be specified")
        return 1

    result = clone_env(
        source=source,
        destinations=destinations,
        overwrite=getattr(args, "overwrite", False),
        dry_run=getattr(args, "dry_run", False),
    )

    if getattr(args, "quiet", False):
        return 0

    print(format_clone_report(result))
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the ``clone`` sub-command with *subparsers*."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "clone",
        help="Clone an env file to one or more destination paths.",
    )
    parser.add_argument(
        "source",
        help="Path to the source .env file.",
    )
    parser.add_argument(
        "destinations",
        nargs="+",
        metavar="DEST",
        help="One or more destination paths.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite destination files that already exist.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        dest="dry_run",
        help="Show what would be written without modifying any files.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress output.",
    )
    parser.set_defaults(func=run)
