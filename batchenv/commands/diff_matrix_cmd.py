"""CLI command: diff-matrix — pairwise diff across multiple .env files."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from batchenv.differ_matrix import diff_matrix, format_diff_matrix_report
from batchenv.parser import parse_env_file


def run(args: argparse.Namespace) -> int:
    paths = [Path(p) for p in args.files]

    missing = [p for p in paths if not p.exists()]
    if missing:
        for m in missing:
            print(f"error: file not found: {m}", file=sys.stderr)
        return 1

    if len(paths) < 2:
        print("error: at least two files are required for diff-matrix", file=sys.stderr)
        return 1

    envs = {}
    for p in paths:
        try:
            envs[p] = parse_env_file(p)
        except Exception as exc:  # noqa: BLE001
            print(f"error: could not parse {p}: {exc}", file=sys.stderr)
            return 1

    result = diff_matrix(envs)
    report = format_diff_matrix_report(result)
    print(report)

    if args.fail_on_diff and result.any_differences:
        return 2
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "diff-matrix",
        help="Show pairwise diffs across multiple .env files.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more .env files to compare.",
    )
    parser.add_argument(
        "--fail-on-diff",
        action="store_true",
        default=False,
        help="Exit with code 2 if any differences are found.",
    )
    parser.set_defaults(func=run)
