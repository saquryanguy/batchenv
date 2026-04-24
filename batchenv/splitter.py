"""Split a merged .env file into multiple files based on key prefixes."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from batchenv.parser import parse_env_file, serialize_env


@dataclass
class SplitResult:
    """Result of a split operation for a single output file."""
    prefix: str
    output_path: Path
    keys: List[str] = field(default_factory=list)
    written: bool = False
    stripped_prefix: bool = True


def split_env(
    env: Dict[str, str],
    prefix: str,
    *,
    strip_prefix: bool = True,
) -> Dict[str, str]:
    """Return entries whose keys start with *prefix*.

    If *strip_prefix* is True the prefix (and an optional trailing underscore)
    is removed from each key in the returned dict.
    """
    result: Dict[str, str] = {}
    sep = prefix if prefix.endswith("_") else prefix + "_"
    for key, value in env.items():
        if key.startswith(sep) or key == prefix:
            if strip_prefix:
                new_key = key[len(sep):] if key.startswith(sep) else key[len(prefix):]
                result[new_key or key] = value
            else:
                result[key] = value
    return result


def split_envs(
    source: Path,
    prefixes: List[str],
    output_dir: Path,
    *,
    strip_prefix: bool = True,
    dry_run: bool = False,
) -> List[SplitResult]:
    """Split *source* .env into one file per prefix inside *output_dir*."""
    env = parse_env_file(source)
    results: List[SplitResult] = []

    for prefix in prefixes:
        subset = split_env(env, prefix, strip_prefix=strip_prefix)
        out_path = output_dir / f".env.{prefix.lower()}"
        result = SplitResult(
            prefix=prefix,
            output_path=out_path,
            keys=list(subset.keys()),
            stripped_prefix=strip_prefix,
        )
        if subset and not dry_run:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(serialize_env(subset))
            result.written = True
        results.append(result)

    return results


def format_split_report(results: List[SplitResult]) -> str:
    lines: List[str] = []
    for r in results:
        status = "written" if r.written else "dry-run / empty"
        lines.append(f"[{r.prefix}] -> {r.output_path}  ({len(r.keys)} keys, {status})")
    return "\n".join(lines) if lines else "No prefixes processed."
