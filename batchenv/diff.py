"""Diff utilities for comparing .env files across directories."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class EnvDiff:
    """Result of diffing two env variable sets."""

    only_in_source: Dict[str, str] = field(default_factory=dict)
    only_in_target: Dict[str, str] = field(default_factory=dict)
    value_changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (src, tgt)
    matching: Set[str] = field(default_factory=set)

    @property
    def has_differences(self) -> bool:
        return bool(self.only_in_source or self.only_in_target or self.value_changed)


def diff_envs(
    source: Dict[str, Optional[str]],
    target: Dict[str, Optional[str]],
) -> EnvDiff:
    """Compare two parsed env dicts and return an EnvDiff."""
    result = EnvDiff()
    all_keys: Set[str] = set(source) | set(target)

    for key in all_keys:
        in_src = key in source
        in_tgt = key in target

        if in_src and not in_tgt:
            result.only_in_source[key] = source[key]
        elif in_tgt and not in_src:
            result.only_in_target[key] = target[key]
        elif source[key] != target[key]:
            result.value_changed[key] = (source[key], target[key])
        else:
            result.matching.add(key)

    return result


def format_diff(diff: EnvDiff, source_label: str = "source", target_label: str = "target") -> List[str]:
    """Return human-readable lines describing the diff."""
    lines: List[str] = []

    for key, val in sorted(diff.only_in_source.items()):
        lines.append(f"- [{source_label} only] {key}={val!r}")

    for key, val in sorted(diff.only_in_target.items()):
        lines.append(f"+ [{target_label} only] {key}={val!r}")

    for key, (src_val, tgt_val) in sorted(diff.value_changed.items()):
        lines.append(f"~ [changed]        {key}: {src_val!r} -> {tgt_val!r}")

    if not lines:
        lines.append("No differences found.")

    return lines
