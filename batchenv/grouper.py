"""Group .env keys by prefix into logical sections."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class GroupResult:
    groups: Dict[str, List[Tuple[str, str]]]  # prefix -> [(key, value)]
    ungrouped: List[Tuple[str, str]]
    changed: bool


def group_env(
    env: Dict[str, str],
    separator: str = "_",
    min_group_size: int = 2,
) -> GroupResult:
    """Group env keys by their prefix (part before the first separator)."""
    prefix_map: Dict[str, List[Tuple[str, str]]] = {}

    for key, value in env.items():
        if separator in key:
            prefix = key.split(separator, 1)[0]
        else:
            prefix = ""
        prefix_map.setdefault(prefix, []).append((key, value))

    groups: Dict[str, List[Tuple[str, str]]] = {}
    ungrouped: List[Tuple[str, str]] = []

    for prefix, pairs in prefix_map.items():
        if prefix and len(pairs) >= min_group_size:
            groups[prefix] = pairs
        else:
            ungrouped.extend(pairs)

    changed = bool(groups)
    return GroupResult(groups=groups, ungrouped=ungrouped, changed=changed)


def group_envs(
    envs: Dict[str, Dict[str, str]],
    separator: str = "_",
    min_group_size: int = 2,
) -> Dict[str, GroupResult]:
    """Apply group_env to multiple env files."""
    return {
        path: group_env(env, separator=separator, min_group_size=min_group_size)
        for path, env in envs.items()
    }


def format_group_report(path: str, result: GroupResult) -> str:
    """Return a human-readable report of grouped keys."""
    lines: List[str] = [f"{path}:"]
    if not result.changed:
        lines.append("  no groups found")
        return "\n".join(lines)
    for prefix, pairs in sorted(result.groups.items()):
        lines.append(f"  [{prefix}] ({len(pairs)} keys)")
        for key, _ in pairs:
            lines.append(f"    {key}")
    if result.ungrouped:
        lines.append(f"  [ungrouped] ({len(result.ungrouped)} keys)")
        for key, _ in result.ungrouped:
            lines.append(f"    {key}")
    return "\n".join(lines)
