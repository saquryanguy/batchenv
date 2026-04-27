"""CLI command: batchenv reference — report variable references in .env files."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from batchenv.referencer import reference_envs, format_reference_report


def run(args: argparse.Namespace) -> int:
    paths: List[Path] = [Path(p) for p in args.files]

    missing_ok: bool = not getattr(args, "strict", False)

    for p in paths:
        if not p.exists():
            print(f"error: file not found: {p}", file=sys.stderr)
            return 1

    results = reference_envs(paths)
    report = format_reference_report(results)
    print(report)

    if not missing_ok:
        for r in results:
            if r.missing_refs:
                return 1

    return 0


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "reference",
        help="Report variable references (${VAR} / $VAR) in .env files.",
    )
    p.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="One or more .env files to inspect.",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with code 1 if any unresolved references are found.",
    )
    p.set_defaults(func=run)
