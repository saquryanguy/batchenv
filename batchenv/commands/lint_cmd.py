import argparse
from pathlib import Path
from batchenv.parser import parse_env_file
from batchenv.linter import lint_envs, format_lint_report


def run(args: argparse.Namespace) -> int:
    paths = [Path(p) for p in args.files]
    missing = [p for p in paths if not p.exists()]
    if missing:
        for m in missing:
            print(f"[ERROR] File not found: {m}")
        return 1

    envs = {}
    for p in paths:
        try:
            envs[str(p)] = parse_env_file(p)
        except Exception as e:
            print(f"[ERROR] Could not parse {p}: {e}")
            return 1

    results = lint_envs(envs)
    report = format_lint_report(results)
    print(report)

    has_errors = any(
        issue.severity == "error"
        for result in results
        for issue in result.issues
    )
    has_warnings = any(result.issues for result in results)

    if has_errors:
        return 2
    if has_warnings and getattr(args, "strict", False):
        return 1
    return 0


def register(subparsers):
    parser = subparsers.add_parser("lint", help="Lint .env files for common issues")
    parser.add_argument("files", nargs="+", help=".env files to lint")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error code on warnings too",
    )
    parser.set_defaults(func=run)
