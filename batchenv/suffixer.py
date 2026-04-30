"""Suffix management for .env keys.

Provides utilities to add, remove, or replace a suffix on environment
variable keys across one or more .env files.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SuffixResult:
    """Result of a suffix operation on a single .env mapping."""

    original: Dict[str, str]
    updated: Dict[str, str]
    added: List[str] = field(default_factory=list)      # new keys that received the suffix
    removed: List[str] = field(default_factory=list)    # old keys that were renamed
    skipped: List[str] = field(default_factory=list)    # keys skipped (already suffixed)

    @property
    def changed(self) -> bool:
        """Return True when at least one key was renamed."""
        return bool(self.added)


def suffix_env(
    env: Dict[str, str],
    suffix: str,
    *,
    keys: Optional[List[str]] = None,
    skip_existing: bool = True,
    strip_existing: Optional[str] = None,
) -> SuffixResult:
    """Append *suffix* to selected keys in *env*.

    Parameters
    ----------
    env:
        Source key/value mapping (not mutated).
    suffix:
        String to append to each key name.
    keys:
        Explicit list of keys to process.  When *None* every key is processed.
    skip_existing:
        When *True* (default) keys that already end with *suffix* are left
        untouched and recorded in ``SuffixResult.skipped``.
    strip_existing:
        Optional suffix to strip from keys *before* appending the new one.
        Useful for replacing one suffix with another in a single pass.
    """
    updated: Dict[str, str] = {}
    added: List[str] = []
    removed: List[str] = []
    skipped: List[str] = []

    target_keys = set(keys) if keys is not None else None

    for key, value in env.items():
        if target_keys is not None and key not in target_keys:
            # Key not in scope — copy verbatim.
            updated[key] = value
            continue

        if skip_existing and key.endswith(suffix):
            updated[key] = value
            skipped.append(key)
            continue

        # Optionally strip an existing suffix first.
        base = key
        if strip_existing and base.endswith(strip_existing):
            base = base[: -len(strip_existing)]

        new_key = base + suffix

        updated[new_key] = value
        added.append(new_key)
        removed.append(key)

    return SuffixResult(
        original=dict(env),
        updated=updated,
        added=added,
        removed=removed,
        skipped=skipped,
    )


def suffix_envs(
    envs: Dict[str, Dict[str, str]],
    suffix: str,
    *,
    keys: Optional[List[str]] = None,
    skip_existing: bool = True,
    strip_existing: Optional[str] = None,
) -> Dict[str, SuffixResult]:
    """Apply :func:`suffix_env` to every file mapping in *envs*.

    Parameters
    ----------
    envs:
        Mapping of file path → key/value dict.

    Returns a mapping of file path → :class:`SuffixResult`.
    """
    return {
        path: suffix_env(
            env,
            suffix,
            keys=keys,
            skip_existing=skip_existing,
            strip_existing=strip_existing,
        )
        for path, env in envs.items()
    }


def format_suffix_report(results: Dict[str, SuffixResult]) -> str:
    """Return a human-readable summary of suffix operations."""
    lines: List[str] = []
    for path, result in results.items():
        if not result.changed:
            lines.append(f"{path}: no changes")
            continue
        lines.append(f"{path}: {len(result.added)} key(s) renamed")
        for old, new in zip(result.removed, result.added):
            lines.append(f"  {old} -> {new}")
        if result.skipped:
            lines.append(f"  skipped (already suffixed): {', '.join(result.skipped)}")
    return "\n".join(lines)
