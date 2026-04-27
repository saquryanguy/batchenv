"""Filter .env entries by key pattern or value pattern."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from batchenv.parser import parse_env_file, serialize_env


@dataclass
class FilterResult:
    path: Path
    original: Dict[str, str]
    filtered: Dict[str, str]
    removed_keys: List[str] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return self.original != self.filtered


def filter_env(
    env: Dict[str, str],
    key_pattern: Optional[str] = None,
    value_pattern: Optional[str] = None,
    invert: bool = False,
) -> Dict[str, str]:
    """Return a copy of env keeping only entries that match the given patterns.

    Args:
        env: Source key/value mapping.
        key_pattern: Regex applied to keys. ``None`` means no key filter.
        value_pattern: Regex applied to values. ``None`` means no value filter.
        invert: When *True*, keep entries that do NOT match (grep -v style).
    """
    key_re = re.compile(key_pattern) if key_pattern else None
    val_re = re.compile(value_pattern) if value_pattern else None

    result: Dict[str, str] = {}
    for k, v in env.items():
        key_match = key_re.search(k) is not None if key_re else True
        val_match = val_re.search(v) is not None if val_re else True
        matches = key_match and val_match
        if invert:
            matches = not matches
        if matches:
            result[k] = v
    return result


def filter_envs(
    paths: List[Path],
    key_pattern: Optional[str] = None,
    value_pattern: Optional[str] = None,
    invert: bool = False,
) -> List[FilterResult]:
    results: List[FilterResult] = []
    for path in paths:
        original = parse_env_file(path)
        filtered = filter_env(original, key_pattern, value_pattern, invert)
        removed = [k for k in original if k not in filtered]
        results.append(FilterResult(path=path, original=original, filtered=filtered, removed_keys=removed))
    return results


def format_filter_report(results: List[FilterResult]) -> str:
    lines: List[str] = []
    for r in results:
        status = "changed" if r.changed else "unchanged"
        lines.append(f"{r.path}: {status} ({len(r.filtered)}/{len(r.original)} keys kept)")
        for k in r.removed_keys:
            lines.append(f"  - removed: {k}")
    return "\n".join(lines)
