"""CLI command: normalize keys in one or more .env files."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from batchenv.parser import parse_env_file, serialize_env
from batchenv.normalizer import normalize_envs, format_normalize_report


def run(args: argparse.Namespace) -> int:
    """Entry-point for the *normalize* sub-command.

    Returns 0 on success, 1 if any error is encountered.
    """
    paths: List[str] = args.files
    dry_run: bool = getattr(args, "dry_run", False)

    envs = {}
    for p in paths:
        path = Path(p)
        if not path.exists():
            print(f"error: file not found: {p}")
            return 1
        envs[p] = parse_env_file(str(path))

    results = normalize_envs(envs)
    report = format_normalize_report(results)
    print(report)

    if dry_run:
        return 0

    for p, result in results.items():
        if result.changed:
            Path(p).write_text(serialize_env(result.normalized))

    return 0


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the *normalize* sub-command with *subparsers*."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "normalize",
        help="Normalize .env key names (uppercase, replace hyphens, strip whitespace).",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="One or more .env files to normalize.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Print what would change without modifying files.",
    )
    parser.set_defaults(func=run)
