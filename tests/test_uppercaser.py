"""Tests for batchenv.uppercaser."""
from pathlib import Path

import pytest

from batchenv.uppercaser import (
    UppercaseResult,
    format_uppercase_report,
    uppercase_env,
    uppercase_envs,
)


# ---------------------------------------------------------------------------
# unit tests for uppercase_env
# ---------------------------------------------------------------------------

def test_lowercase_keys_are_uppercased():
    result = uppercase_env({"foo": "bar", "baz": "qux"})
    assert result.updated == {"FOO": "bar", "BAZ": "qux"}
    assert result.changed is True
    assert ("foo", "FOO") in result.renamed
    assert ("baz", "BAZ") in result.renamed


def test_already_uppercase_keys_unchanged():
    result = uppercase_env({"FOO": "bar", "BAZ": "qux"})
    assert result.updated == {"FOO": "bar", "BAZ": "qux"}
    assert result.changed is False
    assert result.renamed == []


def test_mixed_case_keys():
    result = uppercase_env({"MyKey": "value", "UPPER": "ok"})
    assert "MYKEY" in result.updated
    assert "UPPER" in result.updated
    assert result.changed is True
    assert len(result.renamed) == 1
    assert result.renamed[0] == ("MyKey", "MYKEY")


def test_empty_env():
    result = uppercase_env({})
    assert result.updated == {}
    assert result.changed is False


def test_values_are_preserved():
    result = uppercase_env({"key": "hello world", "other": "123"})
    assert result.updated["KEY"] == "hello world"
    assert result.updated["OTHER"] == "123"


def test_original_is_not_mutated():
    env = {"foo": "bar"}
    uppercase_env(env)
    assert "foo" in env


# ---------------------------------------------------------------------------
# integration tests for uppercase_envs (file I/O)
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def test_uppercase_envs_writes_file(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "foo=bar\nbaz=qux\n")
    results = uppercase_envs([f], dry_run=False)
    assert results[0].changed is True
    content = f.read_text()
    assert "FOO=bar" in content
    assert "BAZ=qux" in content


def test_uppercase_envs_dry_run_does_not_modify(tmp_dir: Path):
    original = "foo=bar\n"
    f = _write(tmp_dir / ".env", original)
    uppercase_envs([f], dry_run=True)
    assert f.read_text() == original


def test_uppercase_envs_no_change_when_already_upper(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "FOO=bar\n")
    results = uppercase_envs([f], dry_run=False)
    assert results[0].changed is False


# ---------------------------------------------------------------------------
# format report
# ---------------------------------------------------------------------------

def test_format_report_no_changes():
    r = UppercaseResult(path=Path(".env"), original={}, updated={}, renamed=[], changed=False)
    report = format_uppercase_report([r])
    assert "no changes" in report


def test_format_report_with_renames():
    r = UppercaseResult(
        path=Path(".env"),
        original={"foo": "bar"},
        updated={"FOO": "bar"},
        renamed=[("foo", "FOO")],
        changed=True,
    )
    report = format_uppercase_report([r])
    assert "1 key(s) uppercased" in report
    assert "'foo'" in report
    assert "'FOO'" in report
