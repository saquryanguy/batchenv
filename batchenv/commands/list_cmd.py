"""List all .env files found under given directories."""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional


def find_env_files(root: str, filename: str = ".env") -> List[Path]:
    """Recursively find all files matching *filename* under *root*."""
    matches: List[Path] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fname in filenames:
            if fname == filename or fname.startswith(filename + "."):
                matches.append(Path(dirpath) / fname)
    return sorted(matches)


def run(
    directories: List[str],
    filename: str = ".env",
    show_keys: bool = False,
    output=None,
) -> None:
    """Entry point for the ``list`` sub-command.

    Args:
        directories: Paths to search.
        filename: Base filename to look for (default ``.env``).
        show_keys: When *True*, print each key found in the file.
        output: File-like object for output (defaults to stdout).
    """
    import sys
    from batchenv.parser import parse_env_file

    out = output or sys.stdout

    for directory in directories:
        env_files = find_env_files(directory, filename)
        if not env_files:
            out.write(f"[{directory}] no env files found\n")
            continue
        for path in env_files:
            out.write(f"{path}\n")
            if show_keys:
                try:
                    data = parse_env_file(str(path))
                    for key in data:
                        out.write(f"  {key}\n")
                except Exception as exc:  # noqa: BLE001
                    out.write(f"  <error reading file: {exc}>\n")
