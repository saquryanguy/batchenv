"""Validation logic for comparing env files against a reference."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ValidationResult:
    path: Path
    missing_keys: list[str] = field(default_factory=list)  # in ref but not target
    extra_keys: list[str] = field(default_factory=list)    # in target but not ref

    @property
    def is_valid(self) -> bool:
        return not self.missing_keys and not self.extra_keys


def validate_envs(
    reference: dict[str, Optional[str]],
    targets: dict[Path, dict[str, Optional[str]]],
    strict: bool = False,
) -> dict[Path, ValidationResult]:
    """Validate each target against the reference env.

    Args:
        reference: parsed reference env.
        targets: mapping of path -> parsed env.
        strict: if True, extra keys in target are also reported.
    """
    ref_keys = set(reference.keys())
    results: dict[Path, ValidationResult] = {}

    for path, env in targets.items():
        target_keys = set(env.keys())
        missing = sorted(ref_keys - target_keys)
        extra = sorted(target_keys - ref_keys) if strict else []
        results[path] = ValidationResult(path=path, missing_keys=missing, extra_keys=extra)

    return results


def format_validation_report(results: dict[Path, ValidationResult]) -> str:
    lines: list[str] = []
    for path, result in results.items():
        if result.is_valid:
            lines.append(f"✔  {path}")
        else:
            lines.append(f"✘  {path}")
            for key in result.missing_keys:
                lines.append(f"   - missing : {key}")
            for key in result.extra_keys:
                lines.append(f"   + extra   : {key}")
    lines.append("")
    return "\n".join(lines)
