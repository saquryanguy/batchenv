"""Strip comments from .env files."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from batchenv.parser import parse_env_file, serialize_env


@dataclass
class StripCommentsResult:
    path: Path
    original_lines: int
    stripped_lines: int
    changed: bool


def strip_comments_env(env: Dict[str, str]) -> Dict[str, str]:
    """Return a copy of env with comment-only entries removed."""
    return {k: v for k, v in env.items() if not k.startswith("#")}


def strip_comments_envs(
    paths: List[Path],
) -> List[StripCommentsResult]:
    results = []
    for path in paths:
        original = parse_env_file(path)
        stripped = strip_comments_env(original)
        changed = len(stripped) != len(original)
        results.append(
            StripCommentsResult(
                path=path,
                original_lines=len(original),
                stripped_lines=len(stripped),
                changed=changed,
            )
        )
    return results


def format_strip_comments_report(results: List[StripCommentsResult]) -> str:
    lines = []
    for r in results:
        status = "changed" if r.changed else "unchanged"
        removed = r.original_lines - r.stripped_lines
        lines.append(f"{r.path}: {status} ({removed} comment(s) removed)")
    return "\n".join(lines)
