"""Patch specific key-value pairs into one or more .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from batchenv.parser import parse_env_file, serialize_env


@dataclass
class PatchResult:
    path: Path
    applied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    changed: bool = False


def patch_env(
    env: Dict[str, str],
    patches: Dict[str, str],
    *,
    overwrite: bool = True,
) -> tuple[Dict[str, str], List[str], List[str]]:
    """Apply *patches* to *env*.

    Returns (updated_env, applied_keys, skipped_keys).
    Keys are skipped when *overwrite* is False and the key already exists.
    """
    result = dict(env)
    applied: List[str] = []
    skipped: List[str] = []

    for key, value in patches.items():
        if key in result and not overwrite:
            skipped.append(key)
        else:
            result[key] = value
            applied.append(key)

    return result, applied, skipped


def patch_envs(
    paths: List[Path],
    patches: Dict[str, str],
    *,
    overwrite: bool = True,
    dry_run: bool = False,
) -> List[PatchResult]:
    """Patch each file in *paths* with *patches*.

    When *dry_run* is True the files are not written.
    """
    results: List[PatchResult] = []

    for path in paths:
        env = parse_env_file(path) if path.exists() else {}
        updated, applied, skipped = patch_env(env, patches, overwrite=overwrite)
        changed = bool(applied)

        if changed and not dry_run:
            path.write_text(serialize_env(updated), encoding="utf-8")

        results.append(PatchResult(path=path, applied=applied, skipped=skipped, changed=changed))

    return results


def format_patch_report(results: List[PatchResult]) -> str:
    lines: List[str] = []
    for r in results:
        status = "changed" if r.changed else "unchanged"
        lines.append(f"{r.path}  [{status}]")
        for k in r.applied:
            lines.append(f"  + {k}")
        for k in r.skipped:
            lines.append(f"  ~ {k} (skipped)")
    return "\n".join(lines)
