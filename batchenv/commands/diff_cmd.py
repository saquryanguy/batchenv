"""CLI command: diff two .env files and print the result."""

import sys
from pathlib import Path
from typing import Optional

from batchenv.parser import parse_env_file
from batchenv.diff import diff_envs, format_diff


def run(
    source_path: str,
    target_path: str,
    source_label: Optional[str] = None,
    target_label: Optional[str] = None,
    exit_nonzero: bool = True,
) -> int:
    """Diff two .env files and print results.  Returns exit code."""
    src = Path(source_path)
    tgt = Path(target_path)

    errors = []
    if not src.exists():
        errors.append(f"Source file not found: {src}")
    if not tgt.exists():
        errors.append(f"Target file not found: {tgt}")

    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 2

    source_env = parse_env_file(src)
    target_env = parse_env_file(tgt)

    src_label = source_label or str(src)
    tgt_label = target_label or str(tgt)

    diff = diff_envs(source_env, target_env)
    lines = format_diff(diff, source_label=src_label, target_label=tgt_label)

    for line in lines:
        print(line)

    if diff.has_differences:
        print(
            f"\nSummary: {len(diff.only_in_source)} only in source, "
            f"{len(diff.only_in_target)} only in target, "
            f"{len(diff.value_changed)} changed, "
            f"{len(diff.matching)} matching."
        )
        return 1 if exit_nonzero else 0

    return 0
