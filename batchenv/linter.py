from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

SUSPICIOUS_PATTERNS = [
    ("localhost", "Value contains 'localhost' — may not be suitable for production"),
    ("127.0.0.1", "Value contains loopback address"),
    ("todo", "Value looks like a placeholder (todo)"),
    ("fixme", "Value looks like a placeholder (fixme)"),
    ("changeme", "Value looks like a default placeholder"),
    ("example.com", "Value contains example domain"),
]


@dataclass
class LintIssue:
    key: str
    message: str
    severity: str = "warning"  # 'warning' | 'error'


@dataclass
class LintResult:
    path: str
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)


def lint_env(env: Dict[str, str], path: str = "") -> LintResult:
    issues: List[LintIssue] = []

    for key, value in env.items():
        if not key.strip():
            issues.append(LintIssue(key=key, message="Empty key detected", severity="error"))
            continue
        if key != key.upper():
            issues.append(LintIssue(key=key, message="Key is not uppercase", severity="warning"))
        if value == "":
            issues.append(LintIssue(key=key, message="Value is empty", severity="warning"))
        lower_val = value.lower()
        for pattern, msg in SUSPICIOUS_PATTERNS:
            if pattern in lower_val:
                issues.append(LintIssue(key=key, message=msg, severity="warning"))
                break

    return LintResult(path=path, issues=issues)


def lint_envs(envs: Dict[str, Dict[str, str]]) -> List[LintResult]:
    return [lint_env(env, path=p) for p, env in envs.items()]


def format_lint_report(results: List[LintResult]) -> str:
    lines = []
    for result in results:
        if not result.issues:
            lines.append(f"[OK] {result.path}")
        else:
            lines.append(f"[LINT] {result.path}")
            for issue in result.issues:
                tag = "ERROR" if issue.severity == "error" else "WARN"
                lines.append(f"  [{tag}] {issue.key}: {issue.message}")
    return "\n".join(lines)
