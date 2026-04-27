"""Highlight keys in .env files by marking them with a comment tag or prefix."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from batchenv.parser import parse_env_file, serialize_env


@dataclass
class HighlightResult:
    path: str
    original: Dict[str, str]
    highlighted: Dict[str, str]
    marked_keys: List[str] = field(default_factory=list)
    changed: bool = False


def highlight_env(
    env: Dict[str, str],
    keys: List[str],
    marker: str = "# [highlighted]",
    overwrite: bool = False,
) -> Dict[str, str]:
    """Return a new env dict where matching keys have *marker* appended to their value.

    The marker is appended as an inline comment separated by a space so the
    serialised file remains valid for most dotenv parsers that strip comments.
    """
    result: Dict[str, str] = {}
    for k, v in env.items():
        if k in keys:
            if not overwrite and marker in v:
                result[k] = v
            else:
                # Strip any pre-existing marker before re-applying
                clean = v.replace(f" {marker}", "").replace(marker, "").rstrip()
                result[k] = f"{clean} {marker}"
        else:
            result[k] = v
    return result


def highlight_envs(
    paths: List[str],
    keys: List[str],
    marker: str = "# [highlighted]",
    overwrite: bool = False,
) -> List[HighlightResult]:
    results: List[HighlightResult] = []
    for path in paths:
        original = parse_env_file(path)
        highlighted = highlight_env(original, keys, marker=marker, overwrite=overwrite)
        marked = [k for k in keys if k in original]
        changed = highlighted != original
        results.append(
            HighlightResult(
                path=path,
                original=original,
                highlighted=highlighted,
                marked_keys=marked,
                changed=changed,
            )
        )
    return results


def format_highlight_report(results: List[HighlightResult]) -> str:
    lines: List[str] = []
    for r in results:
        status = "changed" if r.changed else "unchanged"
        lines.append(f"{r.path}: {status}")
        for k in r.marked_keys:
            lines.append(f"  ~ {k}")
    return "\n".join(lines)
