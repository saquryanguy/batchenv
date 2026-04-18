from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class DedupeResult:
    path: str
    original: Dict[str, str]
    deduped: Dict[str, str]
    removed_duplicates: List[Tuple[str, str]]  # (key, duplicate_value)
    changed: bool


def dedupe_env(path: str, env: Dict[str, str], raw_lines: List[str]) -> DedupeResult:
    """Remove duplicate keys, keeping the last occurrence."""
    seen: Dict[str, List[str]] = {}
    for line in raw_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            seen.setdefault(key, []).append(stripped)

    removed: List[Tuple[str, str]] = []
    for key, occurrences in seen.items():
        if len(occurrences) > 1:
            for dup in occurrences[:-1]:
                val = dup.split("=", 1)[1].strip().strip('"').strip("'")
                removed.append((key, val))

    changed = len(removed) > 0
    return DedupeResult(
        path=path,
        original=dict(env),
        deduped=dict(env),
        removed_duplicates=removed,
        changed=changed,
    )


def dedupe_envs(paths: List[str], envs: List[Dict[str, str]], raw_lines_list: List[List[str]]) -> List[DedupeResult]:
    return [dedupe_env(p, e, r) for p, e, r in zip(paths, envs, raw_lines_list)]


def format_dedupe_report(results: List[DedupeResult]) -> str:
    lines = []
    for r in results:
        if r.changed:
            lines.append(f"{r.path}: removed {len(r.removed_duplicates)} duplicate(s)")
            for key, val in r.removed_duplicates:
                lines.append(f"  - {key}={val}")
        else:
            lines.append(f"{r.path}: no duplicates found")
    return "\n".join(lines)
