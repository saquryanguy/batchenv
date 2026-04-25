import argparse
from pathlib import Path
from batchenv.parser import parse_env_file, serialize_env
from batchenv.redactor import redact_envs, format_redact_report, DEFAULT_PATTERNS


def _parse_patterns(patterns_arg: str | None) -> set[str]:
    """Parse the comma-separated patterns argument into a set of pattern strings.

    Falls back to DEFAULT_PATTERNS if no argument is provided.
    """
    if not patterns_arg:
        return DEFAULT_PATTERNS
    return {p.strip() for p in patterns_arg.split(",") if p.strip()}


def run(args: argparse.Namespace) -> int:
    paths = [Path(p) for p in args.files]
    missing = [p for p in paths if not p.exists()]
    if missing:
        for m in missing:
            print(f"error: file not found: {m}")
        return 1

    patterns = _parse_patterns(args.patterns)
    placeholder = args.placeholder or "***"

    envs = {str(p): parse_env_file(p) for p in paths}
    results = redact_envs(envs, patterns=patterns, placeholder=placeholder)

    if args.dry_run:
        print(format_redact_report(results))
        return 0

    for result in results:
        content = serialize_env(result.redacted)
        Path(result.path).write_text(content)

    print(format_redact_report(results))
    return 0


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("redact", help="Redact sensitive values in .env files")
    p.add_argument("files", nargs="+", help=".env files to redact")
    p.add_argument(
        "--patterns",
        default=None,
        help="Comma-separated substrings to match sensitive keys (default: built-in list)",
    )
    p.add_argument(
        "--placeholder",
        default="***",
        help="Replacement value for redacted keys (default: ***)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print report without modifying files",
    )
    p.set_defaults(func=run)
