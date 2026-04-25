"""Multi-file diff matrix: compare every pair of env files and report differences."""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Tuple

from batchenv.diff import EnvDiff, diff_envs


@dataclass
class PairDiff:
    left: Path
    right: Path
    diff: EnvDiff

    @property
    def has_differences(self) -> bool:
        return bool(
            self.diff.only_in_source
            or self.diff.only_in_target
            or self.diff.value_changed
        )


@dataclass
class DiffMatrixResult:
    pairs: List[PairDiff] = field(default_factory=list)

    @property
    def any_differences(self) -> bool:
        return any(p.has_differences for p in self.pairs)

    @property
    def differing_pairs(self) -> List[PairDiff]:
        return [p for p in self.pairs if p.has_differences]


def diff_matrix(
    envs: Dict[Path, Dict[str, str]],
) -> DiffMatrixResult:
    """Compute pairwise diffs for all combinations of env files."""
    result = DiffMatrixResult()
    paths = list(envs.keys())
    for left, right in combinations(paths, 2):
        d = diff_envs(envs[left], envs[right])
        result.pairs.append(PairDiff(left=left, right=right, diff=d))
    return result


def format_diff_matrix_report(result: DiffMatrixResult) -> str:
    if not result.pairs:
        return "No files to compare."

    lines: List[str] = []
    for pair in result.pairs:
        header = f"[{pair.left.name}] vs [{pair.right.name}]"
        if not pair.has_differences:
            lines.append(f"{header}: identical")
            continue
        lines.append(header)
        for key in sorted(pair.diff.only_in_source):
            lines.append(f"  < {key} (only in {pair.left.name})")
        for key in sorted(pair.diff.only_in_target):
            lines.append(f"  > {key} (only in {pair.right.name})")
        for key, (lv, rv) in sorted(pair.diff.value_changed.items()):
            lines.append(f"  ~ {key}: {lv!r} -> {rv!r}")
    return "\n".join(lines)
