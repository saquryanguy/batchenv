from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from batchenv.parser import parse_env_file


@dataclass
class AuditEntry:
    key: str
    files_present: List[str] = field(default_factory=list)
    files_missing: List[str] = field(default_factory=list)
    values_consistent: bool = True
    distinct_values: int = 0


@dataclass
class AuditReport:
    entries: Dict[str, AuditEntry] = field(default_factory=dict)
    files: List[str] = field(default_factory=list)

    @property
    def inconsistent_keys(self) -> List[str]:
        return [k for k, e in self.entries.items() if not e.values_consistent]

    @property
    def missing_keys(self) -> List[str]:
        return [k for k, e in self.entries.items() if e.files_missing]


def audit_envs(paths: List[Path]) -> AuditReport:
    report = AuditReport(files=[str(p) for p in paths])
    parsed = {str(p): parse_env_file(p) for p in paths}
    all_keys: set = set()
    for env in parsed.values():
        all_keys.update(env.keys())

    for key in sorted(all_keys):
        entry = AuditEntry(key=key)
        values_seen = set()
        for path_str, env in parsed.items():
            if key in env:
                entry.files_present.append(path_str)
                values_seen.add(env[key])
            else:
                entry.files_missing.append(path_str)
        entry.distinct_values = len(values_seen)
        entry.values_consistent = len(values_seen) <= 1
        report.entries[key] = entry

    return report


def format_audit_report(report: AuditReport) -> str:
    lines = [f"Audited {len(report.files)} file(s)\n"]
    for key, entry in report.entries.items():
        status = "OK"
        notes = []
        if entry.files_missing:
            notes.append(f"missing in {len(entry.files_missing)} file(s)")
            status = "WARN"
        if not entry.values_consistent:
            notes.append(f"{entry.distinct_values} distinct values")
            status = "DIFF"
        note_str = "; ".join(notes) if notes else ""
        lines.append(f"  [{status}] {key}" + (f" — {note_str}" if note_str else ""))
    return "\n".join(lines)
