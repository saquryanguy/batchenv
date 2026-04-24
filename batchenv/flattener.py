"""Flatten multiple .env files into a single merged dict, with prefix namespacing."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from batchenv.parser import parse_env_file


@dataclass
class FlattenResult:
    env: Dict[str, str]
    sources: Dict[str, str]  # key -> originating file path
    skipped: List[str] = field(default_factory=list)
    changed: bool = False


def flatten_envs(
    paths: List[Path],
    prefix: Optional[str] = None,
    separator: str = "__",
    overwrite: bool = False,
) -> FlattenResult:
    """Merge *paths* into one dict, optionally prefixing keys with the stem.

    Args:
        paths: ordered list of .env files to flatten.
        prefix: static prefix applied to every key (e.g. ``"APP"``).  When
            *None* the file stem is used as the per-file prefix.
        separator: string placed between prefix and original key.
        overwrite: if *True* later files overwrite earlier values.
    """
    merged: Dict[str, str] = {}
    sources: Dict[str, str] = {}
    skipped: List[str] = []

    for path in paths:
        file_prefix = prefix if prefix is not None else path.stem.upper()
        env = parse_env_file(path)
        for raw_key, value in env.items():
            flat_key = f"{file_prefix}{separator}{raw_key}" if file_prefix else raw_key
            if flat_key in merged and not overwrite:
                skipped.append(flat_key)
                continue
            merged[flat_key] = value
            sources[flat_key] = str(path)

    return FlattenResult(
        env=merged,
        sources=sources,
        skipped=skipped,
        changed=bool(merged),
    )


def format_flatten_report(result: FlattenResult) -> str:
    lines: List[str] = []
    lines.append(f"Flattened {len(result.env)} key(s).")
    if result.skipped:
        lines.append(f"Skipped (duplicate) keys: {', '.join(sorted(result.skipped))}")
    return "\n".join(lines)
