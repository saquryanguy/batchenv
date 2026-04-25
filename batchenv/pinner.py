"""Pin specific keys to fixed values across multiple .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from batchenv.parser import parse_env_file, serialize_env


@dataclass
class PinResult:
    path: Path
    pinned: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    changed: bool = False


def pin_env(
    env: Dict[str, str],
    pins: Dict[str, str],
    overwrite: bool = True,
) -> tuple[Dict[str, str], List[str], List[str]]:
    """Apply pin values to env dict. Returns (new_env, pinned_keys, skipped_keys)."""
    result = dict(env)
    pinned: List[str] = []
    skipped: List[str] = []

    for key, value in pins.items():
        if key in result and not overwrite:
            skipped.append(key)
        else:
            result[key] = value
            pinned.append(key)

    return result, pinned, skipped


def pin_envs(
    paths: List[Path],
    pins: Dict[str, str],
    overwrite: bool = True,
    dry_run: bool = False,
) -> List[PinResult]:
    """Pin keys across multiple .env files."""
    results: List[PinResult] = []

    for path in paths:
        env = parse_env_file(path) if path.exists() else {}
        new_env, pinned, skipped = pin_env(env, pins, overwrite=overwrite)
        changed = new_env != env

        if changed and not dry_run:
            path.write_text(serialize_env(new_env))

        results.append(PinResult(path=path, pinned=pinned, skipped=skipped, changed=changed))

    return results


def format_pin_report(results: List[PinResult]) -> str:
    lines: List[str] = []
    for r in results:
        status = "changed" if r.changed else "unchanged"
        lines.append(f"{r.path}  [{status}]")
        for k in r.pinned:
            lines.append(f"  pinned:  {k}")
        for k in r.skipped:
            lines.append(f"  skipped: {k}")
    return "\n".join(lines)
