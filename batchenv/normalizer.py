"""Normalize .env file keys: uppercase, strip whitespace, replace hyphens with underscores."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class NormalizeResult:
    path: str
    original: Dict[str, str]
    normalized: Dict[str, str]
    changes: List[Tuple[str, str]]  # (old_key, new_key)
    changed: bool = field(init=False)

    def __post_init__(self) -> None:
        self.changed = bool(self.changes)


def _normalize_key(key: str) -> str:
    """Return a normalized version of *key*."""
    return key.strip().upper().replace("-", "_")


def normalize_env(path: str, env: Dict[str, str]) -> NormalizeResult:
    """Normalize all keys in *env* and return a NormalizeResult."""
    normalized: Dict[str, str] = {}
    changes: List[Tuple[str, str]] = []

    for key, value in env.items():
        new_key = _normalize_key(key)
        if new_key != key:
            changes.append((key, new_key))
        # Last writer wins if two keys normalize to the same target.
        normalized[new_key] = value

    return NormalizeResult(
        path=path,
        original=dict(env),
        normalized=normalized,
        changes=changes,
    )


def normalize_envs(
    envs: Dict[str, Dict[str, str]]
) -> Dict[str, NormalizeResult]:
    """Normalize keys for each file in *envs*."""
    return {path: normalize_env(path, env) for path, env in envs.items()}


def format_normalize_report(results: Dict[str, NormalizeResult]) -> str:
    """Return a human-readable summary of normalization results."""
    lines: List[str] = []
    for path, result in results.items():
        if result.changed:
            lines.append(f"{path}: {len(result.changes)} key(s) normalized")
            for old, new in result.changes:
                lines.append(f"  {old!r} -> {new!r}")
        else:
            lines.append(f"{path}: no changes")
    return "\n".join(lines)
