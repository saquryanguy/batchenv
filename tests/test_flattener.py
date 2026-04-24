"""Tests for batchenv.flattener."""
from pathlib import Path

import pytest

from batchenv.flattener import flatten_envs, format_flatten_report


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def test_flatten_basic_with_stem_prefix(tmp_dir):
    a = _write(tmp_dir / "service.env", "HOST=localhost\nPORT=8080\n")
    result = flatten_envs([a])
    assert result.env["SERVICE__HOST"] == "localhost"
    assert result.env["SERVICE__PORT"] == "8080"
    assert result.sources["SERVICE__HOST"] == str(a)


def test_flatten_static_prefix(tmp_dir):
    a = _write(tmp_dir / "db.env", "NAME=mydb\n")
    result = flatten_envs([a], prefix="DB")
    assert "DB__NAME" in result.env


def test_flatten_custom_separator(tmp_dir):
    a = _write(tmp_dir / "app.env", "KEY=val\n")
    result = flatten_envs([a], separator="_")
    assert "APP_KEY" in result.env


def test_flatten_no_prefix(tmp_dir):
    a = _write(tmp_dir / "app.env", "FOO=bar\n")
    result = flatten_envs([a], prefix="")
    assert result.env.get("FOO") == "bar"


def test_flatten_no_overwrite_skips_duplicate(tmp_dir):
    a = _write(tmp_dir / "first.env", "KEY=one\n")
    b = _write(tmp_dir / "second.env", "KEY=two\n")
    result = flatten_envs([a, b], prefix="APP", overwrite=False)
    assert result.env["APP__KEY"] == "one"
    assert "APP__KEY" in result.skipped


def test_flatten_overwrite_replaces_value(tmp_dir):
    a = _write(tmp_dir / "first.env", "KEY=one\n")
    b = _write(tmp_dir / "second.env", "KEY=two\n")
    result = flatten_envs([a, b], prefix="APP", overwrite=True)
    assert result.env["APP__KEY"] == "two"
    assert result.skipped == []


def test_flatten_multiple_files_different_keys(tmp_dir):
    a = _write(tmp_dir / "alpha.env", "A=1\n")
    b = _write(tmp_dir / "beta.env", "B=2\n")
    result = flatten_envs([a, b])
    assert result.env["ALPHA__A"] == "1"
    assert result.env["BETA__B"] == "2"
    assert len(result.env) == 2


def test_flatten_changed_flag(tmp_dir):
    a = _write(tmp_dir / "x.env", "K=v\n")
    result = flatten_envs([a])
    assert result.changed is True


def test_format_flatten_report_no_skipped(tmp_dir):
    a = _write(tmp_dir / "app.env", "KEY=val\n")
    result = flatten_envs([a])
    report = format_flatten_report(result)
    assert "1 key" in report
    assert "Skipped" not in report


def test_format_flatten_report_with_skipped(tmp_dir):
    a = _write(tmp_dir / "svc.env", "X=1\n")
    b = _write(tmp_dir / "other.env", "X=2\n")
    result = flatten_envs([a, b], prefix="P", overwrite=False)
    report = format_flatten_report(result)
    assert "Skipped" in report
    assert "P__X" in report
