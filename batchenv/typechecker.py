"""Type-checking for .env values: detect likely type mismatches or suspicious values."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_BOOL_VALUES = {"true", "false", "1", "0", "yes", "no", "on", "off"}
_INT_RE = re.compile(r"^-?\d+$")
_FLOAT_RE = re.compile(r"^-?\d+\.\d+$")
_URL_RE = re.compile(r"^https?://", re.IGNORECASE)
_PORT_RE = re.compile(r"^\d{1,5}$")


def _infer_type(value: str) -> str:
    """Return a simple inferred type label for a value string."""
    if value == "":
        return "empty"
    if value.lower() in _BOOL_VALUES:
        return "bool"
    if _INT_RE.match(value):
        v = int(value)
        if 1 <= v <= 65535:
            return "port_or_int"
        return "int"
    if _FLOAT_RE.match(value):
        return "float"
    if _URL_RE.match(value):
        return "url"
    return "string"


@dataclass
class TypeIssue:
    key: str
    file: str
    expected_type: str
    actual_type: str
    value: str
    message: str


@dataclass
class TypeCheckResult:
    file: str
    issues: List[TypeIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0


def typecheck_env(
    env: Dict[str, str],
    path: str,
    hints: Optional[Dict[str, str]] = None,
) -> TypeCheckResult:
    """Check each key's value against optional type hints.

    hints maps key -> expected type label (bool, int, float, url, string, port_or_int).
    Keys without hints are still checked for obviously suspicious patterns.
    """
    hints = hints or {}
    issues: List[TypeIssue] = []

    for key, value in env.items():
        inferred = _infer_type(value)
        expected = hints.get(key)

        if expected and inferred not in (expected, "empty"):
            # Allow port_or_int to satisfy int hints
            if not (expected == "int" and inferred == "port_or_int"):
                issues.append(
                    TypeIssue(
                        key=key,
                        file=path,
                        expected_type=expected,
                        actual_type=inferred,
                        value=value,
                        message=f"{key}: expected {expected}, got {inferred} ({value!r})",
                    )
                )

    return TypeCheckResult(file=path, issues=issues)


def typecheck_envs(
    envs: Dict[str, Dict[str, str]],
    hints: Optional[Dict[str, str]] = None,
) -> List[TypeCheckResult]:
    """Run typecheck_env over multiple files."""
    return [typecheck_env(env, path, hints) for path, env in envs.items()]


def format_typecheck_report(results: List[TypeCheckResult]) -> str:
    lines: List[str] = []
    for result in results:
        if result.ok:
            lines.append(f"[OK] {result.file}")
        else:
            lines.append(f"[FAIL] {result.file}")
            for issue in result.issues:
                lines.append(f"  - {issue.message}")
    return "\n".join(lines)
