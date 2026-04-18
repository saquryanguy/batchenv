import argparse
from pathlib import Path
from typing import List

from batchenv.parser import parse_env_file, serialize_env
from batchenv.sorter import sort_envs, format_sort_report


def run(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="batchenv sort",
        description="Sort keys in .env files alphabetically.",
    )
    parser.add_argument("files", nargs="+", help=".env files to sort")
    parser.add_argument(
        "--reverse", action="store_true", help="Sort in descending order"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without writing"
    )
    args = parser.parse_args(argv)

    envs = []
    for f in args.files:
        path = Path(f)
        if not path.exists():
            print(f"error: file not found: {f}")
            return 1
        envs.append((f, parse_env_file(path)))

    results = sort_envs(envs, reverse=args.reverse)
    print(format_sort_report(results))

    if not args.dry_run:
        for r in results:
            if r.changed:
                Path(r.path).write_text(serialize_env(r.sorted_env))

    return 0
