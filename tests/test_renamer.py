"""Tests for batchenv.renamer."""
import pytest
from batchenv.renamer import rename_key, format_rename_report, RenameResult


def _envs():
    return {
        "a.env": {"FOO": "1", "BAR": "2"},
        "b.env": {"FOO": "3", "BAZ": "4"},
        "c.env": {"BAR": "5"},  # old_key missing
    }


def test_rename_basic():
    envs = _envs()
    result = rename_key(envs, "FOO", "NEW_FOO")
    assert "NEW_FOO" in envs["a.env"]
    assert "FOO" not in envs["a.env"]
    assert "NEW_FOO" in envs["b.env"]
    assert "a.env" in result.renamed
    assert "b.env" in result.renamed


def test_rename_skips_missing():
    envs = _envs()
    result = rename_key(envs, "FOO", "NEW_FOO")
    assert "c.env" in result.skipped_missing
    assert "c.env" not in result.renamed


def test_rename_skips_conflict():
    envs = {
        "a.env": {"FOO": "1", "NEW_FOO": "existing"},
    }
    result = rename_key(envs, "FOO", "NEW_FOO")
    assert "a.env" in result.skipped_conflict
    assert envs["a.env"]["FOO"] == "1"  # unchanged


def test_rename_preserves_order():
    envs = {"a.env": {"A": "1", "FOO": "2", "B": "3"}}
    rename_key(envs, "FOO", "NEW_FOO")
    keys = list(envs["a.env"].keys())
    assert keys == ["A", "NEW_FOO", "B"]


def test_success_property():
    envs = {"a.env": {"FOO": "1"}}
    result = rename_key(envs, "FOO", "BAR")
    assert result.success is True


def test_success_false_when_nothing_renamed():
    envs = {"a.env": {"OTHER": "1"}}
    result = rename_key(envs, "FOO", "BAR")
    assert result.success is False


def test_format_rename_report():
    result = RenameResult(
        old_key="FOO",
        new_key="BAR",
        renamed=["a.env"],
        skipped_missing=["b.env"],
        skipped_conflict=["c.env"],
    )
    report = format_rename_report(result)
    assert "FOO" in report
    assert "BAR" in report
    assert "[ok]" in report
    assert "[missing]" in report
    assert "[conflict]" in report
