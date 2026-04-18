"""validate command – check that all target .env files have the same keys as a reference."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from batchenv.parser import parse_env_file
from batchenv.validator import validate_envs, format_validation_report


def run(
    reference: str,
    targets: list[str],
    strict: bool = False,
    quiet: bool = False,
) -> int:
    """Return exit-code: 0 = all valid, 1 = issues found, 2 = error."""
    ref_path = Path(reference)
    if not ref_path.exists():
        print(f"error: reference file not found: {ref_path}", file=sys.stderr)
        return 2

    try:
        ref_env = parse_env_file(ref_path)
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not parse {ref_path}: {exc}", file=sys.stderr)
        return 2

    target_envs: dict[Path, dict[str, Optional[str]]] = {}
    for t in targets:
        tp = Path(t)
        if not tp.exists():
            print(f"warning: target not found, skipping: {tp}", file=sys.stderr)
            continue
        try:
            target_envs[tp] = parse_env_file(tp)
        except Exception as exc:  # noqa: BLE001
            print(f"warning: could not parse {tp}: {exc}", file=sys.stderr)

    if not target_envs:
        print("error: no valid target files to validate", file=sys.stderr)
        return 2

    results = validate_envs(ref_env, target_envs, strict=strict)
    report = format_validation_report(results)

    if not quiet:
        print(report, end="")

    any_issues = any(r.missing_keys or r.extra_keys for r in results.values())
    return 1 if any_issues else 0
