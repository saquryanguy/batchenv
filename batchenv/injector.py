"""Inject key-value pairs from a .env file into the current process environment."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from batchenv.parser import parse_env_file


@dataclass
class InjectResult:
    path: Path
    injected: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    overwritten: List[str] = field(default_factory=list)
    changed: bool = False


def inject_env(
    path: Path,
    *,
    overwrite: bool = False,
    keys: Optional[List[str]] = None,
    dry_run: bool = False,
) -> InjectResult:
    """Inject variables from *path* into ``os.environ``.

    Args:
        path: Path to the .env file to read.
        overwrite: When *True*, existing environment variables are replaced.
        keys: Optional allowlist of keys to inject; all keys are injected when
              *None*.
        dry_run: When *True*, the environment is not actually modified.

    Returns:
        An :class:`InjectResult` describing what was (or would be) changed.
    """
    env: Dict[str, str] = parse_env_file(path)
    result = InjectResult(path=path)

    for key, value in env.items():
        if keys is not None and key not in keys:
            continue

        if key in os.environ:
            if overwrite:
                if not dry_run:
                    os.environ[key] = value
                result.overwritten.append(key)
                result.changed = True
            else:
                result.skipped.append(key)
        else:
            if not dry_run:
                os.environ[key] = value
            result.injected.append(key)
            result.changed = True

    return result


def format_inject_report(results: List[InjectResult]) -> str:
    """Return a human-readable summary of one or more inject operations."""
    lines: List[str] = []
    for r in results:
        lines.append(f"[{r.path}]")
        for k in r.injected:
            lines.append(f"  + {k}  (injected)")
        for k in r.overwritten:
            lines.append(f"  ~ {k}  (overwritten)")
        for k in r.skipped:
            lines.append(f"  - {k}  (skipped, already set)")
        if not r.injected and not r.overwritten and not r.skipped:
            lines.append("  (no variables)")
    return "\n".join(lines)
