"""Rotate (replace) values for specified keys across .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from batchenv.parser import parse_env_file, serialize_env


@dataclass
class RotateResult:
    path: str
    rotated: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    changed: bool = False


def rotate_env(
    path: str,
    rotations: Dict[str, str],
    *,
    only_existing: bool = True,
    dry_run: bool = False,
) -> RotateResult:
    """Apply *rotations* (key -> new_value) to the env file at *path*.

    Args:
        path: Path to the .env file.
        rotations: Mapping of key names to their new values.
        only_existing: When True, skip keys that are not already present.
        dry_run: When True, do not write changes to disk.

    Returns:
        A :class:`RotateResult` describing what changed.
    """
    env = parse_env_file(path)
    result = RotateResult(path=path)

    updated = dict(env)
    for key, new_value in rotations.items():
        if only_existing and key not in updated:
            result.skipped.append(key)
            continue
        if updated.get(key) == new_value:
            result.skipped.append(key)
            continue
        updated[key] = new_value
        result.rotated.append(key)

    if result.rotated:
        result.changed = True
        if not dry_run:
            with open(path, "w") as fh:
                fh.write(serialize_env(updated))

    return result


def rotate_envs(
    paths: List[str],
    rotations: Dict[str, str],
    *,
    only_existing: bool = True,
    dry_run: bool = False,
) -> List[RotateResult]:
    """Apply *rotations* to every file in *paths*."""
    return [
        rotate_env(p, rotations, only_existing=only_existing, dry_run=dry_run)
        for p in paths
    ]


def format_rotate_report(results: List[RotateResult]) -> str:
    """Return a human-readable summary of rotation results."""
    lines: List[str] = []
    for r in results:
        if r.changed:
            lines.append(f"[rotated] {r.path}: {', '.join(r.rotated)}")
        else:
            lines.append(f"[unchanged] {r.path}")
        if r.skipped:
            lines.append(f"  skipped: {', '.join(r.skipped)}")
    return "\n".join(lines)
