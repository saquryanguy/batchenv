"""rename_cmd: rename a key across multiple .env files."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from batchenv.parser import parse_env_file, serialize_env


def run(args: argparse.Namespace) -> int:
    paths: List[Path] = [Path(p) for p in args.files]
    old_key: str = args.old_key
    new_key: str = args.new_key
    dry_run: bool = args.dry_run

    if not paths:
        print("No files specified.")
        return 1

    renamed_in: List[str] = []
    skipped: List[str] = []

    for path in paths:
        if not path.exists():
            print(f"[skip] {path} — file not found")
            skipped.append(str(path))
            continue

        env = parse_env_file(path)

        if old_key not in env:
            skipped.append(str(path))
            continue

        if new_key in env:
            print(f"[skip] {path} — target key '{new_key}' already exists")
            skipped.append(str(path))
            continue

        # Preserve insertion order
        updated = {}
        for k, v in env.items():
            if k == old_key:
                updated[new_key] = v
            else:
                updated[k] = v

        if dry_run:
            print(f"[dry-run] {path}: '{old_key}' -> '{new_key}'")
        else:
            path.write_text(serialize_env(updated))
            print(f"[renamed] {path}: '{old_key}' -> '{new_key}'")

        renamed_in.append(str(path))

    print(f"\nRenamed in {len(renamed_in)} file(s), skipped {len(skipped)}.")
    return 0
