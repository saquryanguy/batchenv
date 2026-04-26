"""Tests for batchenv.rotator."""
import os
import pytest

from batchenv.rotator import rotate_env, rotate_envs, format_rotate_report


@pytest.fixture()
def tmp_dir(tmp_path):
    return tmp_path


def _write(path, content: str) -> str:
    full = str(path)
    with open(full, "w") as fh:
        fh.write(content)
    return full


def test_rotate_basic_key(tmp_dir):
    p = _write(tmp_dir / ".env", "DB_PASS=old\nAPI_KEY=abc\n")
    result = rotate_env(p, {"DB_PASS": "new_secret"})
    assert result.changed is True
    assert "DB_PASS" in result.rotated
    content = open(p).read()
    assert "new_secret" in content


def test_rotate_skips_missing_key_when_only_existing(tmp_dir):
    p = _write(tmp_dir / ".env", "FOO=bar\n")
    result = rotate_env(p, {"MISSING_KEY": "value"}, only_existing=True)
    assert result.changed is False
    assert "MISSING_KEY" in result.skipped


def test_rotate_adds_missing_key_when_not_only_existing(tmp_dir):
    p = _write(tmp_dir / ".env", "FOO=bar\n")
    result = rotate_env(p, {"NEW_KEY": "hello"}, only_existing=False)
    assert result.changed is True
    assert "NEW_KEY" in result.rotated
    assert "hello" in open(p).read()


def test_rotate_dry_run_does_not_modify(tmp_dir):
    p = _write(tmp_dir / ".env", "SECRET=old\n")
    original = open(p).read()
    result = rotate_env(p, {"SECRET": "new"}, dry_run=True)
    assert result.changed is True
    assert open(p).read() == original


def test_rotate_skips_same_value(tmp_dir):
    p = _write(tmp_dir / ".env", "TOKEN=abc123\n")
    result = rotate_env(p, {"TOKEN": "abc123"})
    assert result.changed is False
    assert "TOKEN" in result.skipped


def test_rotate_multiple_keys(tmp_dir):
    p = _write(tmp_dir / ".env", "A=1\nB=2\nC=3\n")
    result = rotate_env(p, {"A": "10", "B": "20"})
    assert result.changed is True
    assert set(result.rotated) == {"A", "B"}
    content = open(p).read()
    assert "10" in content
    assert "20" in content
    assert "3" in content


def test_rotate_envs_multiple_files(tmp_dir):
    p1 = _write(tmp_dir / "a.env", "KEY=old\n")
    p2 = _write(tmp_dir / "b.env", "KEY=old\n")
    results = rotate_envs([p1, p2], {"KEY": "new"})
    assert len(results) == 2
    assert all(r.changed for r in results)
    assert "new" in open(p1).read()
    assert "new" in open(p2).read()


def test_format_rotate_report_changed(tmp_dir):
    p = _write(tmp_dir / ".env", "X=1\n")
    result = rotate_env(p, {"X": "2"})
    report = format_rotate_report([result])
    assert "rotated" in report
    assert "X" in report


def test_format_rotate_report_unchanged(tmp_dir):
    p = _write(tmp_dir / ".env", "X=1\n")
    result = rotate_env(p, {"X": "1"})
    report = format_rotate_report([result])
    assert "unchanged" in report
