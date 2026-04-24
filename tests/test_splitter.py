"""Tests for batchenv.splitter."""
from pathlib import Path

import pytest

from batchenv.splitter import split_env, split_envs, format_split_report


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


# ---------------------------------------------------------------------------
# Unit tests for split_env
# ---------------------------------------------------------------------------

def test_split_env_basic():
    env = {"APP_HOST": "localhost", "APP_PORT": "8080", "DB_URL": "postgres://"}
    result = split_env(env, "APP")
    assert result == {"HOST": "localhost", "PORT": "8080"}


def test_split_env_no_strip_prefix():
    env = {"APP_HOST": "localhost", "DB_URL": "postgres://"}
    result = split_env(env, "APP", strip_prefix=False)
    assert result == {"APP_HOST": "localhost"}


def test_split_env_no_matches():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = split_env(env, "APP")
    assert result == {}


def test_split_env_prefix_with_trailing_underscore():
    env = {"APP_KEY": "val", "OTHER": "x"}
    result = split_env(env, "APP_")
    assert "KEY" in result
    assert "OTHER" not in result


def test_split_env_preserves_values():
    env = {"SVC_SECRET": "abc123", "SVC_DEBUG": "true"}
    result = split_env(env, "SVC")
    assert result["SECRET"] == "abc123"
    assert result["DEBUG"] == "true"


# ---------------------------------------------------------------------------
# Integration tests for split_envs
# ---------------------------------------------------------------------------

def test_split_envs_writes_files(tmp_dir):
    src = _write(tmp_dir / ".env", "APP_HOST=localhost\nDB_URL=postgres://\n")
    results = split_envs(src, ["APP", "DB"], tmp_dir)

    app_file = tmp_dir / ".env.app"
    db_file = tmp_dir / ".env.db"
    assert app_file.exists()
    assert db_file.exists()
    assert "HOST=localhost" in app_file.read_text()
    assert "URL=postgres://" in db_file.read_text()


def test_split_envs_dry_run_does_not_write(tmp_dir):
    src = _write(tmp_dir / ".env", "APP_HOST=localhost\n")
    results = split_envs(src, ["APP"], tmp_dir, dry_run=True)

    assert not (tmp_dir / ".env.app").exists()
    assert results[0].written is False


def test_split_envs_empty_prefix_produces_no_file(tmp_dir):
    src = _write(tmp_dir / ".env", "APP_HOST=localhost\n")
    results = split_envs(src, ["MISSING"], tmp_dir)

    assert not (tmp_dir / ".env.missing").exists()
    assert results[0].written is False
    assert results[0].keys == []


def test_split_envs_keys_listed_in_result(tmp_dir):
    src = _write(tmp_dir / ".env", "SVC_A=1\nSVC_B=2\nOTHER=3\n")
    results = split_envs(src, ["SVC"], tmp_dir)
    assert set(results[0].keys) == {"A", "B"}


# ---------------------------------------------------------------------------
# format_split_report
# ---------------------------------------------------------------------------

def test_format_split_report_written(tmp_dir):
    src = _write(tmp_dir / ".env", "APP_X=1\n")
    results = split_envs(src, ["APP"], tmp_dir)
    report = format_split_report(results)
    assert "APP" in report
    assert "written" in report


def test_format_split_report_empty():
    report = format_split_report([])
    assert report == "No prefixes processed."
