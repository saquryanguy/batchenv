"""Tests for batchenv.differ_summary."""
from __future__ import annotations

from pathlib import Path

import pytest

from batchenv.differ_summary import (
    SummaryEntry,
    SummaryReport,
    format_summary_report,
    summarise_envs,
)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content)
    return p


def test_all_keys_consistent_and_universal(tmp_dir):
    a = _write(tmp_dir / "a.env", "FOO=bar\nBAZ=qux\n")
    b = _write(tmp_dir / "b.env", "FOO=bar\nBAZ=qux\n")
    report = summarise_envs([a, b])
    assert report.all_ok
    assert len(report.entries) == 2


def test_missing_key_detected(tmp_dir):
    a = _write(tmp_dir / "a.env", "FOO=bar\nBAZ=qux\n")
    b = _write(tmp_dir / "b.env", "FOO=bar\n")
    report = summarise_envs([a, b])
    baz = next(e for e in report.entries if e.key == "BAZ")
    assert not baz.is_universal
    assert str(b) in baz.files_missing
    assert report.missing_in_some


def test_inconsistent_values_detected(tmp_dir):
    a = _write(tmp_dir / "a.env", "FOO=one\n")
    b = _write(tmp_dir / "b.env", "FOO=two\n")
    report = summarise_envs([a, b])
    foo = report.entries[0]
    assert not foo.is_consistent
    assert set(foo.unique_values) == {"one", "two"}
    assert report.inconsistent_keys


def test_same_value_is_consistent(tmp_dir):
    a = _write(tmp_dir / "a.env", "KEY=same\n")
    b = _write(tmp_dir / "b.env", "KEY=same\n")
    report = summarise_envs([a, b])
    assert report.entries[0].is_consistent
    assert len(report.entries[0].unique_values) == 1


def test_missing_file_treated_as_empty(tmp_dir):
    a = _write(tmp_dir / "a.env", "FOO=bar\n")
    ghost = tmp_dir / "ghost.env"  # does not exist
    report = summarise_envs([a, ghost])
    foo = report.entries[0]
    assert str(ghost) in foo.files_missing


def test_empty_files_produce_no_entries(tmp_dir):
    a = _write(tmp_dir / "a.env", "")
    b = _write(tmp_dir / "b.env", "")
    report = summarise_envs([a, b])
    assert report.entries == []
    assert report.all_ok


def test_keys_are_sorted(tmp_dir):
    a = _write(tmp_dir / "a.env", "ZZZ=1\nAAA=2\nMMM=3\n")
    report = summarise_envs([a])
    keys = [e.key for e in report.entries]
    assert keys == sorted(keys)


def test_format_summary_report_ok(tmp_dir):
    a = _write(tmp_dir / "a.env", "FOO=bar\n")
    b = _write(tmp_dir / "b.env", "FOO=bar\n")
    report = summarise_envs([a, b])
    out = format_summary_report(report)
    assert "[OK]" in out
    assert "FOO" in out


def test_format_summary_report_warn(tmp_dir):
    a = _write(tmp_dir / "a.env", "FOO=one\n")
    b = _write(tmp_dir / "b.env", "FOO=two\n")
    report = summarise_envs([a, b])
    out = format_summary_report(report)
    assert "[WARN]" in out


def test_format_summary_no_keys():
    report = SummaryReport(entries=[], paths=[])
    assert format_summary_report(report) == "No keys found."
