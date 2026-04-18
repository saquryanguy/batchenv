from dataclasses import dataclass, field
from typing import Dict, List, Set

DEFAULT_PATTERNS = {"PASSWORD", "SECRET", "TOKEN", "KEY", "PRIVATE", "CREDENTIAL"}


@dataclass
class RedactResult:
    path: str
    redacted: Dict[str, str]
    redacted_keys: List[str]


def _should_redact(key: str, patterns: Set[str]) -> bool:
    upper = key.upper()
    return any(p in upper for p in patterns)


def redact_env(
    path: str,
    env: Dict[str, str],
    patterns: Set[str] = DEFAULT_PATTERNS,
    placeholder: str = "***",
) -> RedactResult:
    redacted = {}
    redacted_keys = []
    for k, v in env.items():
        if _should_redact(k, patterns):
            redacted[k] = placeholder
            redacted_keys.append(k)
        else:
            redacted[k] = v
    return RedactResult(path=path, redacted=redacted, redacted_keys=redacted_keys)


def redact_envs(
    envs: Dict[str, Dict[str, str]],
    patterns: Set[str] = DEFAULT_PATTERNS,
    placeholder: str = "***",
) -> List[RedactResult]:
    return [
        redact_env(path, env, patterns, placeholder)
        for path, env in envs.items()
    ]


def format_redact_report(results: List[RedactResult]) -> str:
    lines = []
    for r in results:
        if r.redacted_keys:
            keys = ", ".join(r.redacted_keys)
            lines.append(f"{r.path}: redacted {len(r.redacted_keys)} key(s): {keys}")
        else:
            lines.append(f"{r.path}: nothing to redact")
    return "\n".join(lines)
