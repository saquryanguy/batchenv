"""Summarise differences across multiple .env files into a single report."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Sequence

from batchenv.parser import parse_env_file


@dataclass
class SummaryEntry:
    key: str
    files_present: List[str]
    files_missing: List[str]
    unique_values: List[str]

    @property
    def is_consistent(self) -> bool:
        return len(self.unique_values) <= 1

    @property
    def is_universal(self) -> bool:
        return len(self.files_missing) == 0


@dataclass
class SummaryReport:
    entries: List[SummaryEntry] = field(default_factory=list)
    paths: List[str] = field(default_factory=list)

    @property
    def inconsistent_keys(self) -> List[SummaryEntry]:
        return [e for e in self.entries if not e.is_consistent]

    @property
    def missing_in_some(self) -> List[SummaryEntry]:
        return [e for e in self.entries if not e.is_universal]

    @property
    def all_ok(self) -> bool:
        return not self.inconsistent_keys and not self.missing_in_some


def summarise_envs(paths: Sequence[Path]) -> SummaryReport:
    """Build a cross-file summary for all keys found in *any* of the files."""
    str_paths = [str(p) for p in paths]
    parsed: Dict[str, Dict[str, str]] = {}
    for p in paths:
        try:
            parsed[str(p)] = parse_env_file(p)
        except FileNotFoundError:
            parsed[str(p)] = {}

    all_keys: List[str] = sorted(
        {k for env in parsed.values() for k in env}
    )

    entries: List[SummaryEntry] = []
    for key in all_keys:
        present, missing, values = [], [], []
        for sp in str_paths:
            env = parsed[sp]
            if key in env:
                present.append(sp)
                val = env[key]
                if val not in values:
                    values.append(val)
            else:
                missing.append(sp)
        entries.append(SummaryEntry(key, present, missing, values))

    return SummaryReport(entries=entries, paths=str_paths)


def format_summary_report(report: SummaryReport) -> str:
    if not report.entries:
        return "No keys found."
    lines: List[str] = []
    for e in report.entries:
        status = "OK" if (e.is_consistent and e.is_universal) else "WARN"
        vals = ", ".join(repr(v) for v in e.unique_values) or "(none)"
        missing = ", ".join(e.files_missing) if e.files_missing else "-"
        lines.append(
            f"[{status}] {e.key}: values=[{vals}] missing_in=[{missing}]"
        )
    return "\n".join(lines)
