"""Truncate long values in .env files to a maximum length."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TruncateResult:
    path: str
    original: Dict[str, str]
    truncated: Dict[str, str]
    affected_keys: List[str] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return bool(self.affected_keys)


def truncate_env(
    env: Dict[str, str],
    max_length: int,
    path: str = "<env>",
    suffix: str = "...",
    keys: Optional[List[str]] = None,
) -> TruncateResult:
    """Return a new env dict with values truncated to *max_length* characters.

    Args:
        env: Mapping of key -> value.
        max_length: Maximum allowed value length (inclusive).
        path: Label used in the result (typically a file path).
        suffix: String appended to truncated values (counts toward max_length).
        keys: If provided, only truncate values for these keys.
    """
    if max_length < len(suffix):
        raise ValueError(
            f"max_length ({max_length}) must be >= len(suffix) ({len(suffix)})"
        )

    truncated: Dict[str, str] = {}
    affected: List[str] = []

    for k, v in env.items():
        if keys is not None and k not in keys:
            truncated[k] = v
            continue
        if len(v) > max_length:
            truncated[k] = v[: max_length - len(suffix)] + suffix
            affected.append(k)
        else:
            truncated[k] = v

    return TruncateResult(
        path=path,
        original=dict(env),
        truncated=truncated,
        affected_keys=affected,
    )


def truncate_envs(
    envs: Dict[str, Dict[str, str]],
    max_length: int,
    suffix: str = "...",
    keys: Optional[List[str]] = None,
) -> List[TruncateResult]:
    """Apply :func:`truncate_env` to multiple env dicts keyed by path."""
    return [
        truncate_env(env, max_length=max_length, path=path, suffix=suffix, keys=keys)
        for path, env in envs.items()
    ]


def format_truncate_report(results: List[TruncateResult]) -> str:
    lines: List[str] = []
    for r in results:
        if r.changed:
            keys_str = ", ".join(r.affected_keys)
            lines.append(f"{r.path}: truncated {len(r.affected_keys)} key(s): {keys_str}")
        else:
            lines.append(f"{r.path}: no values truncated")
    return "\n".join(lines)
