"""Scope filtering: keep only keys matching a given prefix or pattern."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScopeResult:
    path: str
    original: Dict[str, str]
    filtered: Dict[str, str]
    removed_keys: List[str] = field(default_factory=list)
    changed: bool = False


def scope_env(
    env: Dict[str, str],
    path: str,
    prefix: Optional[str] = None,
    pattern: Optional[str] = None,
    strip_prefix: bool = False,
) -> ScopeResult:
    """Return only keys that match *prefix* or *pattern*.

    Args:
        env: Parsed key/value mapping.
        path: Source file path (used for reporting).
        prefix: Keep keys that start with this string (case-sensitive).
        pattern: Keep keys matching this regex.
        strip_prefix: When *prefix* is given, remove the prefix from kept keys.
    """
    if prefix is None and pattern is None:
        raise ValueError("At least one of 'prefix' or 'pattern' must be provided.")

    compiled = re.compile(pattern) if pattern else None

    filtered: Dict[str, str] = {}
    removed: List[str] = []

    for key, value in env.items():
        keep = False
        if prefix and key.startswith(prefix):
            keep = True
        if compiled and compiled.search(key):
            keep = True

        if keep:
            new_key = key[len(prefix):] if (strip_prefix and prefix and key.startswith(prefix)) else key
            filtered[new_key] = value
        else:
            removed.append(key)

    return ScopeResult(
        path=path,
        original=dict(env),
        filtered=filtered,
        removed_keys=removed,
        changed=bool(removed),
    )


def scope_envs(
    envs: Dict[str, Dict[str, str]],
    prefix: Optional[str] = None,
    pattern: Optional[str] = None,
    strip_prefix: bool = False,
) -> List[ScopeResult]:
    """Apply :func:`scope_env` to multiple files."""
    return [
        scope_env(env, path, prefix=prefix, pattern=pattern, strip_prefix=strip_prefix)
        for path, env in envs.items()
    ]


def format_scope_report(results: List[ScopeResult]) -> str:
    lines: List[str] = []
    for r in results:
        status = "changed" if r.changed else "unchanged"
        lines.append(f"{r.path}: {status} ({len(r.filtered)} kept, {len(r.removed_keys)} removed)")
        for k in r.removed_keys:
            lines.append(f"  - {k}")
    return "\n".join(lines)
