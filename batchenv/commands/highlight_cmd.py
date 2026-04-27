"""CLI command: highlight — mark specific keys in .env files."""
from __future__ import annotations

import argparse
import sys
from typing import List

from batchenv.highlighter import format_highlight_report, highlight_envs
from batchenv.parser import serialize_env


def run(args: argparse.Namespace) -> int:
    """Entry point for the *highlight* sub-command.

    Returns an exit code (0 = success, 1 = error).
    """
    paths: List[str] = args.files
    keys: List[str] = args.keys
    marker: str = getattr(args, "marker", "# [highlighted]")
    overwrite: bool = getattr(args, "overwrite", False)
    dry_run: bool = getattr(args, "dry_run", False)

    if not paths:
        print("highlight: no files specified", file=sys.stderr)
        return 1

    if not keys:
        print("highlight: no keys specified (use --keys)", file=sys.stderr)
        return 1

    results = highlight_envs(paths, keys=keys, marker=marker, overwrite=overwrite)

    for result in results:
        if result.changed and not dry_run:
            try:
                content = serialize_env(result.highlighted)
                with open(result.path, "w") as fh:
                    fh.write(content)
            except OSError as exc:
                print(f"highlight: cannot write {result.path}: {exc}", file=sys.stderr)
                return 1

    print(format_highlight_report(results))
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "highlight",
        help="Mark specific keys in .env files with an inline comment tag.",
    )
    parser.add_argument("files", nargs="+", metavar="FILE", help=".env files to process")
    parser.add_argument(
        "--keys",
        nargs="+",
        required=True,
        metavar="KEY",
        help="Keys to highlight",
    )
    parser.add_argument(
        "--marker",
        default="# [highlighted]",
        metavar="MARKER",
        help="Inline comment marker to append (default: '# [highlighted]')",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-apply marker even if already present",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Preview changes without writing files",
    )
    parser.set_defaults(func=run)
