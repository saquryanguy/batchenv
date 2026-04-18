"""Merge multiple .env files into one, with conflict resolution strategies."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple


class MergeStrategy(str, Enum):
    FIRST = "first"   # keep value from first file that defines the key
    LAST = "last"     # keep value from last file that defines the key
    ERROR = "error"   # raise on conflicting values


@dataclass
class MergeConflict:
    key: str
    values: List[Tuple[str, str]]  # list of (source_path, value)


@dataclass
class MergeResult:
    merged: Dict[str, str] = field(default_factory=dict)
    conflicts: List[MergeConflict] = field(default_factory=list)


def merge_envs(
    sources: List[Tuple[str, Dict[str, str]]],
    strategy: MergeStrategy = MergeStrategy.FIRST,
) -> MergeResult:
    """Merge env dicts from multiple sources.

    Args:
        sources: list of (label, env_dict) pairs.
        strategy: conflict resolution strategy.

    Returns:
        MergeResult with merged dict and any conflicts.
    """
    result: Dict[str, str] = {}
    seen: Dict[str, List[Tuple[str, str]]] = {}

    for label, env in sources:
        for key, value in env.items():
            seen.setdefault(key, []).append((label, value))

    conflicts: List[MergeConflict] = []

    for key, occurrences in seen.items():
        unique_values = list(dict.fromkeys(v for _, v in occurrences))
        if len(unique_values) == 1:
            result[key] = unique_values[0]
        else:
            conflicts.append(MergeConflict(key=key, values=occurrences))
            if strategy == MergeStrategy.ERROR:
                raise ValueError(
                    f"Conflict on key '{key}': "
                    + ", ".join(f"{src}={val!r}" for src, val in occurrences)
                )
            elif strategy == MergeStrategy.FIRST:
                result[key] = occurrences[0][1]
            else:  # LAST
                result[key] = occurrences[-1][1]

    return MergeResult(merged=result, conflicts=conflicts)


def format_merge_report(result: MergeResult) -> str:
    if not result.conflicts:
        return "No conflicts. Merged {} keys.".format(len(result.merged))
    lines = ["Conflicts detected:"]
    for c in result.conflicts:
        lines.append(f"  {c.key}:")
        for src, val in c.values:
            lines.append(f"    {src} -> {val!r}")
    lines.append(f"Total merged keys: {len(result.merged)}")
    return "\n".join(lines)
