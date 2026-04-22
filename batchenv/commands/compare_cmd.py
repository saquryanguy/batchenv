"""CLI command: compare multiple .env files in a matrix view."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from batchenv.parser import parse_env_file
from batchenv.comparator import compare_envs, format_compare_report


def run(args: argparse.Namespace) -> int:
    """Entry point for the compare command.

    Args:
        args: parsed CLI arguments with attributes:
            files  – list of .env file paths to compare
            only_missing – if True, show only keys absent from at least one file
            only_common  – if True, show only keys present in all files

    Returns:
        0 on success, 1 if any partial (missing) keys exist, 2 on error.
    """
    paths: List[Path] = [Path(p) for p in args.files]

    envs = {}
    for path in paths:
        if not path.exists():
            print(f"[error] File not found: {path}", file=sys.stderr)
            return 2
        try:
            envs[str(path)] = parse_env_file(path)
        except Exception as exc:  # noqa: BLE001
            print(f"[error] Cannot parse {path}: {exc}", file=sys.stderr)
            return 2

    result = compare_envs(envs)

    # Optional filtering
    if getattr(args, "only_missing", False):
        result.all_keys = [k for k in result.all_keys if k in result.unique_keys]
    elif getattr(args, "only_common", False):
        result.all_keys = [k for k in result.all_keys if k in result.common_keys]

    print(format_compare_report(result))

    return 1 if result.unique_keys else 0


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the compare sub-command."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "compare",
        help="Compare multiple .env files in a matrix view",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more .env files to compare",
    )
    parser.add_argument(
        "--only-missing",
        action="store_true",
        default=False,
        help="Show only keys that are absent from at least one file",
    )
    parser.add_argument(
        "--only-common",
        action="store_true",
        default=False,
        help="Show only keys present in every file",
    )
    parser.set_defaults(func=run)
