"""Export merged/resolved env variables to a single output file or stdout."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

from batchenv.parser import parse_env_file, serialize_env
from batchenv.merger import merge_envs, MergeStrategy


def run(
    sources: List[str],
    output: Optional[str] = None,
    strategy: str = "first",
    export_prefix: bool = False,
) -> int:
    """
    Merge *sources* env files and write result to *output* (or stdout).

    Returns exit code (0 = success, 1 = error).
    """
    if not sources:
        print("error: at least one source file is required", file=sys.stderr)
        return 1

    try:
        merge_strategy = MergeStrategy[strategy.upper()]
    except KeyError:
        valid = ", ".join(s.name.lower() for s in MergeStrategy)
        print(f"error: unknown strategy '{strategy}'. Choose from: {valid}", file=sys.stderr)
        return 1

    envs: List[dict] = []
    for src in sources:
        path = Path(src)
        if not path.exists():
            print(f"error: file not found: {src}", file=sys.stderr)
            return 1
        envs.append(parse_env_file(path))

    try:
        result = merge_envs(envs, strategy=merge_strategy)
    except Exception as exc:  # MergeConflict with ERROR strategy
        print(f"error: {exc}", file=sys.stderr)
        return 1

    lines = serialize_env(result.merged, export_prefix=export_prefix)

    if output:
        Path(output).write_text(lines)
        print(f"Exported {len(result.merged)} keys to {output}")
    else:
        sys.stdout.write(lines)

    return 0
