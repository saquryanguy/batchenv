"""CLI command: substitute values across .env files."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

from batchenv.parser import parse_env_file, serialize_env
from batchenv.substitutor import substitute_envs, format_substitute_report


def _parse_replacements(pairs: List[str]) -> Dict[str, str]:
    """Parse 'OLD=NEW' strings into a replacement dict."""
    result: Dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise argparse.ArgumentTypeError(
                f"Invalid replacement pair {pair!r}; expected OLD=NEW"
            )
        old, new = pair.split("=", 1)
        result[old] = new
    return result


def run(args: argparse.Namespace) -> int:
    files: List[str] = args.files
    try:
        replacements = _parse_replacements(args.replace)
    except argparse.ArgumentTypeError as exc:
        print(f"error: {exc}")
        return 1

    if not replacements:
        print("error: at least one --replace OLD=NEW pair is required")
        return 1

    keys = args.keys if args.keys else None

    envs: Dict[str, Dict[str, str]] = {}
    for f in files:
        p = Path(f)
        if not p.exists():
            print(f"error: file not found: {f}")
            return 1
        envs[f] = parse_env_file(p)

    results = substitute_envs(envs, replacements, keys=keys)

    if args.dry_run:
        print(format_substitute_report(results))
        return 0

    for result in results:
        if result.changed:
            Path(result.path).write_text(serialize_env(result.updated))

    print(format_substitute_report(results))
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "substitute",
        help="Substitute specific values across one or more .env files",
    )
    p.add_argument("files", nargs="+", help=".env files to process")
    p.add_argument(
        "--replace",
        metavar="OLD=NEW",
        action="append",
        default=[],
        help="Value substitution pair (repeatable)",
    )
    p.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        help="Limit substitution to these keys only",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print report without writing files",
    )
    p.set_defaults(func=run)
