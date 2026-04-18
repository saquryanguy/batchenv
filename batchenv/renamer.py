"""renamer: core logic for renaming keys across parsed env dicts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class RenameResult:
    old_key: str
    new_key: str
    renamed: List[str] = field(default_factory=list)
    skipped_missing: List[str] = field(default_factory=list)
    skipped_conflict: List[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.renamed) > 0


def rename_key(
    envs: Dict[str, Dict[str, str]],
    old_key: str,
    new_key: str,
) -> RenameResult:
    """Rename *old_key* to *new_key* in each env dict (in-place).

    Returns a RenameResult describing what happened per file label.
    """
    result = RenameResult(old_key=old_key, new_key=new_key)

    for label, env in envs.items():
        if old_key not in env:
            result.skipped_missing.append(label)
            continue
        if new_key in env:
            result.skipped_conflict.append(label)
            continue

        # Rebuild preserving order
        updated = {}
        for k, v in env.items():
            updated[new_key if k == old_key else k] = v
        env.clear()
        env.update(updated)
        result.renamed.append(label)

    return result


def format_rename_report(result: RenameResult) -> str:
    lines = [f"Rename '{result.old_key}' -> '{result.new_key}'"]
    for label in result.renamed:
        lines.append(f"  [ok]       {label}")
    for label in result.skipped_missing:
        lines.append(f"  [missing]  {label}")
    for label in result.skipped_conflict:
        lines.append(f"  [conflict] {label}")
    return "\n".join(lines)
