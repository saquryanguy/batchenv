"""copy_cmd: copy specific keys from one .env file to another."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

from batchenv.parser import parse_env_file, serialize_env


def run(
    source: str,
    target: str,
    keys: List[str],
    *,
    overwrite: bool = False,
    dry_run: bool = False,
    fill_value: Optional[str] = None,
) -> int:
    """Copy *keys* from *source* into *target*.

    Returns 0 on success, 1 on error.
    """
    src_path = Path(source)
    tgt_path = Path(target)

    if not src_path.exists():
        print(f"[error] source file not found: {src_path}", file=sys.stderr)
        return 1

    src_env = parse_env_file(src_path)
    tgt_env = parse_env_file(tgt_path) if tgt_path.exists() else {}

    copied: list[str] = []
    skipped: list[str] = []
    missing: list[str] = []

    for key in keys:
        if key not in src_env:
            if fill_value is not None:
                value = fill_value
                missing.append(key)
            else:
                print(f"[warn] key '{key}' not found in source, skipping", file=sys.stderr)
                skipped.append(key)
                continue
        else:
            value = src_env[key]

        if key in tgt_env and not overwrite:
            print(f"[warn] key '{key}' already exists in target, skipping (use --overwrite)", file=sys.stderr)
            skipped.append(key)
            continue

        tgt_env[key] = value
        copied.append(key)

    print(f"Copied {len(copied)} key(s), skipped {len(skipped)}, filled {len(missing)} missing.")

    if dry_run:
        print("[dry-run] no changes written.")
        return 0

    tgt_path.write_text(serialize_env(tgt_env))
    return 0
