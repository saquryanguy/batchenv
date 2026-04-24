"""CLI command: profile — show statistics about .env files."""
from __future__ import annotations

import argparse
from pathlib import Path

from batchenv.parser import parse_env_file
from batchenv.profiler import profile_envs, format_profile_report


def run(args: argparse.Namespace) -> int:
    """Entry point for the `profile` sub-command."""
    paths = [Path(p) for p in args.files]

    missing = [p for p in paths if not p.exists()]
    if missing:
        for m in missing:
            print(f"error: file not found: {m}")
        return 1

    envs: dict[str, dict[str, str]] = {}
    for path in paths:
        try:
            envs[str(path)] = parse_env_file(path)
        except Exception as exc:  # noqa: BLE001
            print(f"error: could not parse {path}: {exc}")
            return 1

    results = profile_envs(envs)
    report = format_profile_report(results)
    print(report, end="")
    return 0


def register(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser(
        "profile",
        help="Show statistics and metrics for one or more .env files.",
    )
    p.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Path(s) to .env file(s) to profile.",
    )
    p.set_defaults(func=run)
