"""Substitute values in .env files using a key=value mapping."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class SubstituteResult:
    path: str
    original: Dict[str, str]
    updated: Dict[str, str]
    substitutions: List[Tuple[str, str, str]] = field(default_factory=list)  # (key, old, new)
    changed: bool = False


def substitute_env(
    env: Dict[str, str],
    replacements: Dict[str, str],
    keys: List[str] | None = None,
) -> SubstituteResult:
    """Replace specific values across an env dict.

    Args:
        env: Parsed env dict.
        replacements: Mapping of old_value -> new_value.
        keys: If provided, only substitute within these keys.
    """
    updated = dict(env)
    substitutions: List[Tuple[str, str, str]] = []

    target_keys = keys if keys is not None else list(env.keys())

    for key in target_keys:
        if key not in updated:
            continue
        old_val = updated[key]
        if old_val in replacements:
            new_val = replacements[old_val]
            updated[key] = new_val
            substitutions.append((key, old_val, new_val))

    return SubstituteResult(
        path="",
        original=dict(env),
        updated=updated,
        substitutions=substitutions,
        changed=bool(substitutions),
    )


def substitute_envs(
    envs: Dict[str, Dict[str, str]],
    replacements: Dict[str, str],
    keys: List[str] | None = None,
) -> List[SubstituteResult]:
    results = []
    for path, env in envs.items():
        result = substitute_env(env, replacements, keys=keys)
        result.path = path
        results.append(result)
    return results


def format_substitute_report(results: List[SubstituteResult]) -> str:
    lines: List[str] = []
    for r in results:
        if r.changed:
            lines.append(f"{r.path}: {len(r.substitutions)} substitution(s)")
            for key, old, new in r.substitutions:
                lines.append(f"  {key}: {old!r} -> {new!r}")
        else:
            lines.append(f"{r.path}: no changes")
    return "\n".join(lines)
