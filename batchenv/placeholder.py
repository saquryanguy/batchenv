from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class PlaceholderResult:
    path: str
    filled: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)
    changed: bool = False


def fill_placeholders(
    env: Dict[str, str],
    values: Dict[str, str],
    overwrite: bool = False,
) -> tuple[Dict[str, str], Dict[str, str], List[str]]:
    """Replace empty or placeholder values with provided values."""
    result = dict(env)
    filled: Dict[str, str] = {}
    skipped: List[str] = []

    for key, value in values.items():
        if key not in result:
            skipped.append(key)
            continue
        current = result[key].strip()
        if current == "" or current == "PLACEHOLDER" or overwrite:
            result[key] = value
            filled[key] = value
        else:
            skipped.append(key)

    return result, filled, skipped


def fill_envs(
    envs: Dict[str, Dict[str, str]],
    values: Dict[str, str],
    overwrite: bool = False,
) -> List[PlaceholderResult]:
    results = []
    for path, env in envs.items():
        updated, filled, skipped = fill_placeholders(env, values, overwrite=overwrite)
        results.append(
            PlaceholderResult(
                path=path,
                filled=filled,
                skipped=skipped,
                changed=bool(filled),
            )
        )
    return results


def format_placeholder_report(results: List[PlaceholderResult]) -> str:
    lines = []
    for r in results:
        status = "changed" if r.changed else "unchanged"
        lines.append(f"{r.path}: {status}")
        for k, v in r.filled.items():
            lines.append(f"  filled: {k}={v}")
        for k in r.skipped:
            lines.append(f"  skipped: {k}")
    return "\n".join(lines)
