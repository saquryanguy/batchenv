"""CLI command: merge multiple .env files into a single output file."""
from __future__ import annotations
import sys
from pathlib import Path
from typing import List, Optional

from batchenv.parser import parse_env_file, serialize_env
from batchenv.merger import merge_envs, MergeStrategy, format_merge_report


def run(
    sources: List[str],
    output: Optional[str] = None,
    strategy: str = "first",
    dry_run: bool = False,
    quiet: bool = False,
) -> int:
    """Merge source .env files.

    Returns exit code (0 = success, 1 = conflicts with error strategy).
    """
    try:
        merge_strategy = MergeStrategy(strategy)
    except ValueError:
        print(f"Unknown strategy '{strategy}'. Choose: first, last, error.", file=sys.stderr)
        return 2

    parsed_sources = []
    for src in sources:
        path = Path(src)
        if not path.exists():
            print(f"File not found: {src}", file=sys.stderr)
            return 2
        parsed_sources.append((src, parse_env_file(path)))

    try:
        result = merge_envs(parsed_sources, merge_strategy)
    except ValueError as exc:
        print(f"Merge error: {exc}", file=sys.stderr)
        return 1

    if not quiet:
        print(format_merge_report(result))

    if dry_run:
        if not quiet:
            print("[dry-run] No files written.")
        return 0

    content = serialize_env(result.merged)

    if output:
        Path(output).write_text(content)
        if not quiet:
            print(f"Written to {output}")
    else:
        sys.stdout.write(content)

    return 0
