from pathlib import Path
import pytest
from batchenv.auditor import audit_envs, format_audit_report, AuditReport


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def _write(p: Path, content: str):
    p.write_text(content)


def test_all_keys_consistent(tmp_dir):
    a = tmp_dir / "a.env"
    b = tmp_dir / "b.env"
    _write(a, "FOO=bar\nBAZ=qux\n")
    _write(b, "FOO=bar\nBAZ=qux\n")
    report = audit_envs([a, b])
    assert report.inconsistent_keys == []
    assert report.missing_keys == []


def test_missing_key_detected(tmp_dir):
    a = tmp_dir / "a.env"
    b = tmp_dir / "b.env"
    _write(a, "FOO=bar\nBAZ=qux\n")
    _write(b, "FOO=bar\n")
    report = audit_envs([a, b])
    assert "BAZ" in report.missing_keys
    entry = report.entries["BAZ"]
    assert str(b) in entry.files_missing
    assert str(a) in entry.files_present


def test_inconsistent_values(tmp_dir):
    a = tmp_dir / "a.env"
    b = tmp_dir / "b.env"
    _write(a, "FOO=one\n")
    _write(b, "FOO=two\n")
    report = audit_envs([a, b])
    assert "FOO" in report.inconsistent_keys
    assert report.entries["FOO"].distinct_values == 2


def test_consistent_values_not_flagged(tmp_dir):
    a = tmp_dir / "a.env"
    b = tmp_dir / "b.env"
    _write(a, "FOO=same\n")
    _write(b, "FOO=same\n")
    report = audit_envs([a, b])
    assert "FOO" not in report.inconsistent_keys
    assert report.entries["FOO"].values_consistent is True


def test_format_report_contains_keys(tmp_dir):
    a = tmp_dir / "a.env"
    b = tmp_dir / "b.env"
    _write(a, "FOO=one\nBAR=x\n")
    _write(b, "FOO=two\n")
    report = audit_envs([a, b])
    out = format_audit_report(report)
    assert "FOO" in out
    assert "BAR" in out
    assert "DIFF" in out
    assert "WARN" in out


def test_single_file_no_issues(tmp_dir):
    a = tmp_dir / "a.env"
    _write(a, "KEY=value\n")
    report = audit_envs([a])
    assert report.inconsistent_keys == []
    assert report.missing_keys == []


def test_empty_files(tmp_dir):
    a = tmp_dir / "a.env"
    b = tmp_dir / "b.env"
    _write(a, "")
    _write(b, "")
    report = audit_envs([a, b])
    assert report.entries == {}
