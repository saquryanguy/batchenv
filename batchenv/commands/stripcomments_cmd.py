"""CLI command: strip-comments — remove comments from .env files."""
from pathlib import Path
from typing import List

from batchenv.commentstripper import strip_comments_envs, format_strip_comments_report
from batchenv.parser import parse_env_file, serialize_env
from batchenv.commentstripper import strip_comments_env


def run(
    paths: List[str],
    dry_run: bool = False,
    quiet: bool = False,
) -> int:
    """Strip comments from one or more .env files.

    Returns 0 on success, 1 if any file could not be processed.
    """
    resolved = [Path(p) for p in paths]
    missing = [p for p in resolved if not p.exists()]
    if missing:
        for m in missing:
            print(f"error: file not found: {m}")
        return 1

    results = strip_comments_envs(resolved)

    if not dry_run:
        for path, result in zip(resolved, results):
            if result.changed:
                env = parse_env_file(path)
                cleaned = strip_comments_env(env)
                path.write_text(serialize_env(cleaned))

    if not quiet:
        print(format_strip_comments_report(results))

    return 0
