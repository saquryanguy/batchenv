import argparse
from pathlib import Path
from batchenv.parser import parse_env_file, serialize_env
from batchenv.deduplicator import dedupe_envs, format_dedupe_report


def run(args: argparse.Namespace) -> int:
    paths = [Path(p) for p in args.files]
    missing = [p for p in paths if not p.exists()]
    if missing:
        for m in missing:
            print(f"Error: file not found: {m}")
        return 1

    envs = [parse_env_file(str(p)) for p in paths]
    raw_lines_list = [p.read_text().splitlines(keepends=True) for p in paths]

    results = dedupe_envs([str(p) for p in paths], envs, raw_lines_list)
    print(format_dedupe_report(results))

    if args.dry_run:
        return 0

    for result, path in zip(results, paths):
        if result.changed:
            path.write_text(serialize_env(result.deduped))

    return 0


def register(subparsers):
    parser = subparsers.add_parser(
        "dedupe",
        help="Remove duplicate keys from .env files",
    )
    parser.add_argument("files", nargs="+", help=".env files to deduplicate")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Report duplicates without modifying files",
    )
    parser.set_defaults(func=run)
