"""Clone an env file to one or more destination paths, optionally overwriting."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from batchenv.parser import parse_env_file, serialize_env


@dataclass
class CloneResult:
    source: Path
    destinations: List[Path] = field(default_factory=list)
    skipped: List[Path] = field(default_factory=list)
    changed: bool = False


def clone_env(
    source: Path,
    destinations: List[Path],
    overwrite: bool = False,
    dry_run: bool = False,
) -> CloneResult:
    """Copy *source* env to every path in *destinations*.

    Skips destinations that already exist unless *overwrite* is True.
    When *dry_run* is True nothing is written to disk.
    """
    env: Dict[str, str] = parse_env_file(source)
    result = CloneResult(source=source)

    for dest in destinations:
        if dest.exists() and not overwrite:
            result.skipped.append(dest)
            continue
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(serialize_env(env), encoding="utf-8")
        result.destinations.append(dest)
        result.changed = True

    return result


def format_clone_report(result: CloneResult) -> str:
    lines: List[str] = [f"source: {result.source}"]
    if result.destinations:
        lines.append("cloned to:")
        for d in result.destinations:
            lines.append(f"  {d}")
    if result.skipped:
        lines.append("skipped (already exist):")
        for s in result.skipped:
            lines.append(f"  {s}")
    if not result.changed:
        lines.append("no files written")
    return "\n".join(lines)
