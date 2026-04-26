"""CLI command: pin — force specific key=value pairs across .env files."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from batchenv.pinner import format_pin_report, pin_envs


def _parse_pins(pairs: List[str]) -> dict[str, str]:
    """Parse KEY=VALUE strings into a dict.

    Raises a user-friendly error and exits if any pair is malformed or if
    a key is empty after stripping whitespace.
    """
    pins: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            print(f"[error] invalid pin format (expected KEY=VALUE): {pair}", file=sys.stderr)
            sys.exit(1)
        key, _, value = pair.partition("=")
        key = key.strip()
        if not key:
            print(f"[error] pin key must not be empty: {pair!r}", file=sys.stderr)
            sys.exit(1)
        pins[key] = value
    return pins


def run(args: argparse.Namespace) -> int:
    paths = [Path(p) for p in args.files]
    missing = [p for p in paths if not p.exists()]
    if missing:
        for p in missing:
            print(f"[error] file not found: {p}", file=sys.stderr)
        return 1

    pins = _parse_pins(args.pin)
    if not pins:
        print("[error] at least one --pin KEY=VALUE is required", file=sys.stderr)
        return 1

    results = pin_envs(
        paths,
        pins,
        overwrite=not args.no_overwrite,
        dry_run=args.dry_run,
    )

    print(format_pin_report(results))
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "pin",
        help="Force specific key=value pairs across one or more .env files.",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help="Target .env files")
    p.add_argument(
        "--pin",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Key-value pair to pin (repeatable)",
    )
    p.add_argument(
        "--no-overwrite",
        action="store_true",
        default=False,
        help="Skip keys that already exist",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview changes without writing files",
    )
    p.set_defaults(func=run)
