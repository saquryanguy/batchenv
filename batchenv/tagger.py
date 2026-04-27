"""Tag keys in .env files with inline comments for categorisation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class TagResult:
    path: str
    original: Dict[str, str]
    tagged: Dict[str, str]  # key -> "value  # tag"
    keys_tagged: List[str] = field(default_factory=list)
    changed: bool = False


def _strip_existing_tag(value: str) -> str:
    """Remove any trailing inline comment from a value."""
    if "  #" in value:
        return value[: value.index("  #")].rstrip()
    return value


def tag_env(
    path: str,
    env: Dict[str, str],
    tags: Dict[str, str],
    overwrite: bool = False,
) -> TagResult:
    """Apply *tags* (key -> comment text) to matching keys in *env*.

    The tag is appended as an inline comment: ``VALUE  # <tag>``.
    If *overwrite* is False, keys that already carry a comment are skipped.
    """
    tagged: Dict[str, str] = {}
    keys_tagged: List[str] = []

    for key, value in env.items():
        if key in tags:
            has_comment = "  #" in value
            if has_comment and not overwrite:
                tagged[key] = value
            else:
                clean = _strip_existing_tag(value)
                new_value = f"{clean}  # {tags[key]}"
                tagged[key] = new_value
                keys_tagged.append(key)
        else:
            tagged[key] = value

    return TagResult(
        path=path,
        original=dict(env),
        tagged=tagged,
        keys_tagged=keys_tagged,
        changed=bool(keys_tagged),
    )


def tag_envs(
    envs: List[Tuple[str, Dict[str, str]]],
    tags: Dict[str, str],
    overwrite: bool = False,
) -> List[TagResult]:
    return [tag_env(path, env, tags, overwrite=overwrite) for path, env in envs]


def format_tag_report(results: List[TagResult]) -> str:
    lines: List[str] = []
    for r in results:
        status = "changed" if r.changed else "unchanged"
        lines.append(f"{r.path}: {status}")
        for k in r.keys_tagged:
            lines.append(f"  + {k}  # {r.tagged[k].split('  #', 1)[1].strip()}")
    return "\n".join(lines)
