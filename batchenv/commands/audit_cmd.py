from __future__ import annotations
import argparse
from pathlib import Path
from typing import List

from batchenv.auditor import audit_envs, format_audit_report


def run(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="batchenv audit",
        description="Audit .env files for missing or inconsistent keys.",
    )
    parser.add_argument("files", nargs="+", help=".env files to audit")
    parser.add_argument(
        "--fail-on-diff",
        action="store_true",
        help="Exit with non-zero code if any key has inconsistent values",
    )
    parser.add_argument(
        "--fail-on-missing",
        action="store_true",
        help="Exit with non-zero code if any key is missing in some files",
    )
    args = parser.parse_args(argv)

    paths = [Path(f) for f in args.files]
    missing = [p for p in paths if not p.exists()]
    if missing:
        for m in missing:
            print(f"Error: file not found: {m}")
        return 1

    report = audit_envs(paths)
    print(format_audit_report(report))

    if args.fail_on_diff and report.inconsistent_keys:
        return 2
    if args.fail_on_missing and report.missing_keys:
        return 3
    return 0
