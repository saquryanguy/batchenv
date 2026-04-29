"""Prefix all keys in one or more .env files with a given string."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from batchenv.parser import parse_env_file, serialize_env


@dataclass
class PrefixResult:
    path: Path
    original: Dict[str, str]
    prefixed: Dict[str, str]
    changed: bool
    skipped_keys: List[str] = field(default_factory=list)


def prefix_env(
    env: Dict[str, str],
    prefix: str,
    *,
    skip_already_prefixed: bool = True,
) -> PrefixResult:
    """Return a new env dict with *prefix* prepended to every key.

    Args:
        env: Source key/value mapping.
        prefix: String to prepend to each key.
        skip_already_prefixed: When *True* (default) keys that already start
            with *prefix* are left unchanged and recorded in *skipped_keys*.
    """
    prefixed: Dict[str, str] = {}
    skipped: List[str] = []

    for key, value in env.items():
        if skip_already_prefixed and key.startswith(prefix):
            prefixed[key] = value
            skipped.append(key)
        else:
            prefixed[f"{prefix}{key}"] = value

    changed = prefixed != env
    return PrefixResult(
        path=Path("<memory>"),
        original=dict(env),
        prefixed=prefixed,
        changed=changed,
        skipped_keys=skipped,
    )


def prefix_envs(
    paths: List[Path],
    prefix: str,
    *,
    skip_already_prefixed: bool = True,
) -> List[PrefixResult]:
    """Apply :func:`prefix_env` to each file in *paths*."""
    results: List[PrefixResult] = []
    for path in paths:
        env = parse_env_file(path)
        result = prefix_env(env, prefix, skip_already_prefixed=skip_already_prefixed)
        result.path = path
        results.append(result)
    return results


def format_prefix_report(results: List[PrefixResult]) -> str:
    """Return a human-readable summary of prefix operations."""
    lines: List[str] = []
    for r in results:
        status = "changed" if r.changed else "unchanged"
        lines.append(f"{r.path}: {status}")
        if r.skipped_keys:
            skipped = ", ".join(r.skipped_keys)
            lines.append(f"  skipped (already prefixed): {skipped}")
    return "\n".join(lines)
