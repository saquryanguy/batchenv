"""Strip comments and blank lines from parsed .env mappings."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class StripResult:
    original: dict[str, str]
    stripped: dict[str, str]
    changed: bool
    removed_count: int


def strip_env(env: dict[str, str]) -> StripResult:
    """Return a new env dict with comment/blank pseudo-keys removed.

    parse_env_file stores comment lines and blank lines as keys starting
    with '#' or as empty-string keys; strip those out.
    """
    stripped = {
        k: v
        for k, v in env.items()
        if k and not k.startswith("#")
    }
    removed = len(env) - len(stripped)
    return StripResult(
        original=env,
        stripped=stripped,
        changed=removed > 0,
        removed_count=removed,
    )


def strip_envs(
    envs: dict[Path, dict[str, str]]
) -> dict[Path, StripResult]:
    return {path: strip_env(env) for path, env in envs.items()}


def format_strip_report(results: dict[Path, StripResult]) -> str:
    lines: list[str] = []
    for path, result in results.items():
        if result.changed:
            lines.append(
                f"  {path}: removed {result.removed_count} comment/blank line(s)"
            )
        else:
            lines.append(f"  {path}: nothing to strip")
    if not lines:
        return "Nothing to strip."
    return "Strip report:\n" + "\n".join(lines)
