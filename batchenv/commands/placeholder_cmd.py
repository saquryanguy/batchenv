from __future__ import annotations
import argparse
import sys
from pathlib import Path
from batchenv.parser import parse_env_file, serialize_env
from batchenv.placeholder import fill_envs, format_placeholder_report


def run(args: argparse.Namespace) -> int:
    values: dict[str, str] = {}
    for pair in args.set or []:
        if "=" not in pair:
            print(f"Invalid key=value pair: {pair}", file=sys.stderr)
            return 1
        k, v = pair.split("=", 1)
        values[k.strip()] = v.strip()

    if not values:
        print("No values provided via --set.", file=sys.stderr)
        return 1

    envs: dict[str, dict[str, str]] = {}
    for p in args.files:
        path = Path(p)
        if not path.exists():
            print(f"File not found: {p}", file=sys.stderr)
            return 1
        envs[p] = parse_env_file(path)

    results = fill_envs(envs, values, overwrite=args.overwrite)

    print(format_placeholder_report(results))

    if args.dry_run:
        return 0

    for result in results:
        if result.changed:
            path = Path(result.path)
            updated_env = {**envs[result.path], **result.filled}
            path.write_text(serialize_env(updated_env))

    return 0


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "placeholder", help="Fill placeholder/empty values in .env files"
    )
    p.add_argument("files", nargs="+", help=".env files to update")
    p.add_argument(
        "--set", nargs="+", metavar="KEY=VALUE", help="Values to fill"
    )
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing values")
    p.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    p.set_defaults(func=run)
