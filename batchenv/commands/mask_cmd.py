"""CLI command: mask — replace env values with a redaction placeholder."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from batchenv.masker import DEFAULT_MASK, format_mask_report, mask_envs
from batchenv.parser import parse_env_file, serialize_env


def run(args: argparse.Namespace) -> int:  # noqa: C901
    """Entry point for the *mask* sub-command.

    Exit codes:
        0 — success (or dry-run)
        1 — one or more input files could not be read
    """
    paths: List[str] = args.files
    keys: List[str] | None = args.keys or None
    mask: str = args.mask
    visible_chars: int = args.visible_chars
    dry_run: bool = args.dry_run
    output: str | None = getattr(args, "output", None)

    envs = {}
    for p in paths:
        try:
            envs[p] = parse_env_file(p)
        except FileNotFoundError:
            print(f"error: file not found: {p}", file=sys.stderr)
            return 1
        except OSError as exc:
            print(f"error: cannot read {p}: {exc}", file=sys.stderr)
            return 1

    results = mask_envs(envs, keys=keys, mask=mask, visible_chars=visible_chars)

    if dry_run:
        print(format_mask_report(results))
        return 0

    if output and len(results) == 1:
        # Single-file mode: write masked content to a separate output path.
        content = serialize_env(results[0].masked)
        Path(output).write_text(content, encoding="utf-8")
        print(format_mask_report(results))
        return 0

    for result in results:
        content = serialize_env(result.masked)
        Path(result.path).write_text(content, encoding="utf-8")

    print(format_mask_report(results))
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "mask",
        help="Replace env values with a redaction placeholder.",
    )
    parser.add_argument("files", nargs="+", metavar="FILE", help=".env file(s) to mask")
    parser.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        default=None,
        help="Specific keys to mask (default: all keys).",
    )
    parser.add_argument(
        "--mask",
        default=DEFAULT_MASK,
        metavar="PLACEHOLDER",
        help=f"Mask string (default: {DEFAULT_MASK!r}).",
    )
    parser.add_argument(
        "--visible-chars",
        type=int,
        default=0,
        dest="visible_chars",
        metavar="N",
        help="Leave N trailing characters of the value visible.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Print report without writing any files.",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help="Write masked output to FILE instead of overwriting (single-file mode).",
    )
    parser.set_defaults(func=run)
