from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class TrimResult:
    path: str
    original: Dict[str, str]
    trimmed: Dict[str, str]
    removed_keys: List[str] = field(default_factory=list)
    changed: bool = False


def trim_env(path: str, env: Dict[str, str], reference: Dict[str, str]) -> TrimResult:
    """Remove keys from env that are not present in reference."""
    removed = [k for k in env if k not in reference]
    trimmed = {k: v for k, v in env.items() if k in reference}
    return TrimResult(
        path=path,
        original=dict(env),
        trimmed=trimmed,
        removed_keys=removed,
        changed=len(removed) > 0,
    )


def trim_envs(
    envs: Dict[str, Dict[str, str]], reference: Dict[str, str]
) -> List[TrimResult]:
    """Trim multiple env dicts against a reference key set."""
    return [trim_env(path, env, reference) for path, env in envs.items()]


def format_trim_report(results: List[TrimResult]) -> str:
    lines = []
    for r in results:
        if r.changed:
            lines.append(f"{r.path}: removed {len(r.removed_keys)} key(s): {', '.join(r.removed_keys)}")
        else:
            lines.append(f"{r.path}: no changes")
    return "\n".join(lines)
