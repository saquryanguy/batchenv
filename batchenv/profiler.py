"""Profile .env files to produce a statistical summary of their contents.

Provides key counts, value length stats, comment density, blank line ratio,
and detection of common patterns (URLs, secrets-like values, booleans, etc.).
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from batchenv.parser import parse_env_file

# Patterns used to classify values
_URL_RE = re.compile(r"^https?://", re.IGNORECASE)
_BOOL_VALUES = {"true", "false", "yes", "no", "1", "0", "on", "off"}
_SECRET_RE = re.compile(
    r"(password|secret|token|key|api_key|apikey|auth|credential|passwd|pwd)",
    re.IGNORECASE,
)


@dataclass
class ProfileResult:
    """Statistical profile of a single .env file."""

    path: Path
    total_lines: int
    blank_lines: int
    comment_lines: int
    key_count: int
    empty_value_count: int
    url_value_count: int
    bool_value_count: int
    secret_key_count: int
    value_lengths: List[int] = field(default_factory=list)

    # ------------------------------------------------------------------ #
    # Derived metrics
    # ------------------------------------------------------------------ #

    @property
    def blank_ratio(self) -> float:
        if self.total_lines == 0:
            return 0.0
        return self.blank_lines / self.total_lines

    @property
    def comment_ratio(self) -> float:
        if self.total_lines == 0:
            return 0.0
        return self.comment_lines / self.total_lines

    @property
    def avg_value_length(self) -> float:
        if not self.value_lengths:
            return 0.0
        return statistics.mean(self.value_lengths)

    @property
    def max_value_length(self) -> int:
        return max(self.value_lengths, default=0)

    @property
    def min_value_length(self) -> int:
        return min(self.value_lengths, default=0)


def profile_env_file(path: Path) -> ProfileResult:
    """Analyse a single .env file and return a :class:`ProfileResult`."""
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    total_lines = len(raw_lines)
    blank_lines = sum(1 for ln in raw_lines if ln.strip() == "")
    comment_lines = sum(1 for ln in raw_lines if ln.strip().startswith("#"))

    env: Dict[str, str] = parse_env_file(path)
    key_count = len(env)
    empty_value_count = sum(1 for v in env.values() if v == "")
    url_value_count = sum(1 for v in env.values() if _URL_RE.match(v))
    bool_value_count = sum(1 for v in env.values() if v.lower() in _BOOL_VALUES)
    secret_key_count = sum(1 for k in env.keys() if _SECRET_RE.search(k))
    value_lengths = [len(v) for v in env.values()]

    return ProfileResult(
        path=path,
        total_lines=total_lines,
        blank_lines=blank_lines,
        comment_lines=comment_lines,
        key_count=key_count,
        empty_value_count=empty_value_count,
        url_value_count=url_value_count,
        bool_value_count=bool_value_count,
        secret_key_count=secret_key_count,
        value_lengths=value_lengths,
    )


def profile_envs(paths: List[Path]) -> List[ProfileResult]:
    """Profile multiple .env files and return one result per file."""
    return [profile_env_file(p) for p in paths]


def format_profile_report(results: List[ProfileResult]) -> str:
    """Render a human-readable profile report for one or more files."""
    if not results:
        return "No files to profile."

    lines: List[str] = []
    for r in results:
        lines.append(f"File: {r.path}")
        lines.append(f"  Total lines   : {r.total_lines}")
        lines.append(f"  Blank lines   : {r.blank_lines} ({r.blank_ratio:.1%})")
        lines.append(f"  Comment lines : {r.comment_lines} ({r.comment_ratio:.1%})")
        lines.append(f"  Keys          : {r.key_count}")
        lines.append(f"  Empty values  : {r.empty_value_count}")
        lines.append(f"  URL values    : {r.url_value_count}")
        lines.append(f"  Bool values   : {r.bool_value_count}")
        lines.append(f"  Secret-like   : {r.secret_key_count}")
        if r.value_lengths:
            lines.append(
                f"  Value length  : avg={r.avg_value_length:.1f}"
                f"  min={r.min_value_length}  max={r.max_value_length}"
            )
        lines.append("")

    return "\n".join(lines).rstrip()
