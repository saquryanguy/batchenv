"""trim command: remove keys from target .env files not present in a reference file."""
from __future__ import annotations

import argparse
from pathlib import Path

from batchenv.parser import parse_env_file, serialize_env
from batchenv.trimmer import trim_envs, format_trim_report


def run(args: argparse.Namespace) -> int:
    ref_path = Path(args.reference)
    if not ref_path.exists():
        print(f"Error: reference file not found: {ref_path}")
        return 1

    reference = parse_env_file(ref_path)

    targets: dict[str, dict[str, str]] = {}
    for t in args.targets:
        p = Path(t)
        if not p.exists():
            print(f"Warning: target not found, skipping: {p}")
            continue
        targets[str(p)] = parse_env_file(p)

    if not targets:
        print("No valid target files.")
        return 1

    results = trim_envs(targets, reference)
    print(format_trim_report(results))

    if args.dry_run:
        return 0

    for result in results:
        if result.changed:
            Path(result.path).write_text(serialize_env(result.trimmed))

    return 0


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "trim",
        help="Remove keys not present in a reference .env file from target files.",
    )
    parser.add_argument("reference", help="Reference .env file defining allowed keys.")
    parser.add_argument("targets", nargs="+", help="Target .env files to trim.")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without writing files."
    )
    parser.set_defaults(func=run)
