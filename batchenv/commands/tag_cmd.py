"""CLI command: tag — annotate .env keys with inline comments."""
from __future__ import annotations

import argparse
import sys
from typing import Dict, List

from batchenv.parser import parse_env_file, serialize_env
from batchenv.tagger import format_tag_report, tag_envs


def _parse_tag_pairs(raw: List[str]) -> Dict[str, str]:
    """Parse ``KEY=comment text`` strings into a dict."""
    result: Dict[str, str] = {}
    for item in raw:
        if "=" not in item:
            raise argparse.ArgumentTypeError(
                f"Tag spec must be KEY=comment, got: {item!r}"
            )
        key, _, comment = item.partition("=")
        result[key.strip()] = comment.strip()
    return result


def run(args: argparse.Namespace) -> int:
    try:
        tags = _parse_tag_pairs(args.tag or [])
    except argparse.ArgumentTypeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not tags:
        print("error: at least one --tag KEY=comment is required", file=sys.stderr)
        return 1

    envs = []
    for path in args.files:
        try:
            envs.append((path, parse_env_file(path)))
        except FileNotFoundError:
            print(f"error: file not found: {path}", file=sys.stderr)
            return 1

    results = tag_envs(envs, tags, overwrite=args.overwrite)

    if args.dry_run:
        print(format_tag_report(results))
        return 0

    for result in results:
        if result.changed:
            with open(result.path, "w") as fh:
                fh.write(serialize_env(result.tagged))

    print(format_tag_report(results))
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("tag", help="Annotate .env keys with inline comments")
    p.add_argument("files", nargs="+", metavar="FILE")
    p.add_argument(
        "--tag",
        action="append",
        metavar="KEY=comment",
        help="Key and comment to apply (repeatable)",
    )
    p.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing inline comments",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Print changes without writing files",
    )
    p.set_defaults(func=run)
