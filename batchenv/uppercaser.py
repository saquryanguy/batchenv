"""Uppercase all keys in .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

from batchenv.parser import parse_env_file, serialize_env


@dataclass
class UppercaseResult:
    path: Path
    original: Dict[str, str]
    updated: Dict[str, str]
    renamed: List[Tuple[str, str]] = field(default_factory=list)  # (old, new)
    changed: bool = False


def uppercase_env(env: Dict[str, str]) -> UppercaseResult:
    """Return a new env dict with all keys uppercased."""
    updated: Dict[str, str] = {}
    renamed: List[Tuple[str, str]] = []

    for key, value in env.items():
        upper = key.upper()
        updated[upper] = value
        if upper != key:
            renamed.append((key, upper))

    return UppercaseResult(
        path=Path("<memory>"),
        original=dict(env),
        updated=updated,
        renamed=renamed,
        changed=bool(renamed),
    )


def uppercase_envs(
    paths: List[Path],
    dry_run: bool = False,
) -> List[UppercaseResult]:
    """Uppercase keys in each file on disk, optionally writing back."""
    results: List[UppercaseResult] = []
    for path in paths:
        env = parse_env_file(path)
        result = uppercase_env(env)
        result.path = path
        if result.changed and not dry_run:
            path.write_text(serialize_env(result.updated))
        results.append(result)
    return results


def format_uppercase_report(results: List[UppercaseResult]) -> str:
    lines: List[str] = []
    for r in results:
        if not r.changed:
            lines.append(f"{r.path}: no changes")
        else:
            lines.append(f"{r.path}: {len(r.renamed)} key(s) uppercased")
            for old, new in r.renamed:
                lines.append(f"  {old!r} -> {new!r}")
    return "\n".join(lines)
