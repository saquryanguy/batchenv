"""sync command: copy missing keys from a source .env to one or more target .env files."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from batchenv.parser import parse_env_file, serialize_env
from batchenv.diff import diff_envs


def run(
    source: str,
    targets: list[str],
    dry_run: bool = False,
    fill_value: Optional[str] = None,
    overwrite: bool = False,
) -> int:
    """Sync missing (or changed) keys from *source* into every *target* file.

    Returns exit code: 0 = success, 1 = error.
    """
    source_path = Path(source)
    if not source_path.exists():
        print(f"error: source file not found: {source}", file=sys.stderr)
        return 1

    source_env = parse_env_file(source_path)
    exit_code = 0

    for target in targets:
        target_path = Path(target)
        if not target_path.exists():
            print(f"warning: target not found, skipping: {target}", file=sys.stderr)
            exit_code = 1
            continue

        target_env = parse_env_file(target_path)
        diff = diff_envs(source_env, target_env)

        changes: dict[str, str] = {}

        for key in diff.only_in_source:
            changes[key] = fill_value if fill_value is not None else source_env[key]

        if overwrite:
            for key in diff.value_changed:
                changes[key] = fill_value if fill_value is not None else source_env[key]

        if not changes:
            print(f"{target}: already in sync")
            continue

        if dry_run:
            for key, value in changes.items():
                print(f"{target}: [dry-run] would set {key}={value!r}")
            continue

        merged = {**target_env, **changes}
        target_path.write_text(serialize_env(merged))
        print(f"{target}: synced {len(changes)} key(s): {', '.join(changes)}")

    return exit_code
