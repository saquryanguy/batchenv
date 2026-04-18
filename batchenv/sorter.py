from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class SortResult:
    path: str
    original: Dict[str, str]
    sorted_env: Dict[str, str]
    changed: bool


def sort_env(env: Dict[str, str], reverse: bool = False) -> Dict[str, str]:
    """Return a new dict with keys sorted alphabetically."""
    return dict(sorted(env.items(), key=lambda x: x[0], reverse=reverse))


def sort_envs(
    envs: List[Tuple[str, Dict[str, str]]],
    reverse: bool = False,
) -> List[SortResult]:
    """Sort keys in multiple env dicts, returning SortResult per file."""
    results = []
    for path, env in envs:
        sorted_env = sort_env(env, reverse=reverse)
        changed = list(env.keys()) != list(sorted_env.keys())
        results.append(SortResult(path=path, original=env, sorted_env=sorted_env, changed=changed))
    return results


def format_sort_report(results: List[SortResult]) -> str:
    lines = []
    for r in results:
        if r.changed:
            lines.append(f"  sorted: {r.path}")
        else:
            lines.append(f"  unchanged: {r.path}")
    return "\n".join(lines) if lines else "  nothing to sort"
