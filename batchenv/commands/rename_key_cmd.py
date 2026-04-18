"""rename-key command: rename a key across multiple .env files."""
from __future__ import annotations

import argparse
from pathlib import Path

from batchenv.parser import parse_env_file, serialize_env
from batchenv.renamer import rename_key, format_rename_report


def run(args: argparse.Namespace) -> int:
    paths = [Path(p) for p in args.files]
    missing = [p for p in paths if not p.exists()]
    if missing:
        for p in missing:
            print(f"[error] file not found: {p}")
        return 1

    results = {}
    for path in paths:
        env = parse_env_file(path)
        result = rename_key(env, args.old_key, args.new_key, force=args.force)
        results[path] = result

    print(format_rename_report(results))

    if args.dry_run:
        return 0

    for path, result in results.items():
        if result.changed:
            path.write_text(serialize_env(result.env))

    return 0


def register(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("rename-key", help="Rename a key across .env files")
    p.add_argument("old_key", help="Key to rename")
    p.add_argument("new_key", help="New key name")
    p.add_argument("files", nargs="+", help="Target .env files")
    p.add_argument("--force", action="store_true", help="Overwrite new_key if it already exists")
    p.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    p.set_defaults(func=run)
