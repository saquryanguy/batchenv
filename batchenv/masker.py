"""Mask env values by replacing characters with a fixed pattern."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

DEFAULT_MASK = "***"
DEFAULT_VISIBLE_CHARS = 0


@dataclass
class MaskResult:
    path: str
    original: Dict[str, str]
    masked: Dict[str, str]
    keys_masked: List[str] = field(default_factory=list)
    changed: bool = False


def mask_env(
    env: Dict[str, str],
    path: str,
    keys: Optional[List[str]] = None,
    mask: str = DEFAULT_MASK,
    visible_chars: int = DEFAULT_VISIBLE_CHARS,
) -> MaskResult:
    """Return a copy of *env* with selected (or all) values masked.

    Args:
        env: Parsed env mapping.
        path: Source file path (used for reporting only).
        keys: Explicit list of keys to mask. If *None*, all keys are masked.
        mask: Replacement string for hidden portion.
        visible_chars: Number of trailing characters to leave visible.
    """
    masked: Dict[str, str] = {}
    keys_masked: List[str] = []

    target_keys = set(keys) if keys is not None else set(env.keys())

    for key, value in env.items():
        if key in target_keys and value:
            if visible_chars > 0 and len(value) > visible_chars:
                masked[key] = mask + value[-visible_chars:]
            else:
                masked[key] = mask
            keys_masked.append(key)
        else:
            masked[key] = value

    return MaskResult(
        path=path,
        original=dict(env),
        masked=masked,
        keys_masked=keys_masked,
        changed=bool(keys_masked),
    )


def mask_envs(
    envs: Dict[str, Dict[str, str]],
    keys: Optional[List[str]] = None,
    mask: str = DEFAULT_MASK,
    visible_chars: int = DEFAULT_VISIBLE_CHARS,
) -> List[MaskResult]:
    """Apply :func:`mask_env` to multiple files."""
    return [
        mask_env(env, path, keys=keys, mask=mask, visible_chars=visible_chars)
        for path, env in envs.items()
    ]


def format_mask_report(results: List[MaskResult]) -> str:
    lines: List[str] = []
    for r in results:
        status = f"{len(r.keys_masked)} key(s) masked" if r.changed else "no changes"
        lines.append(f"{r.path}: {status}")
        for k in r.keys_masked:
            lines.append(f"  {k}")
    return "\n".join(lines)
