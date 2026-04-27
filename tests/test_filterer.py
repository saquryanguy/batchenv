"""Tests for batchenv.filterer."""
from pathlib import Path

import pytest

from batchenv.filterer import filter_env, filter_envs, format_filter_report


# ---------------------------------------------------------------------------
# filter_env unit tests
# ---------------------------------------------------------------------------

def test_filter_by_key_pattern_keeps_matching():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_NAME": "myapp"}
    result = filter_env(env, key_pattern=r"^DB_")
    assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_filter_by_value_pattern_keeps_matching():
    env = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
    result = filter_env(env, value_pattern=r"^\d+$")
    assert result == {"PORT": "5432"}


def test_filter_by_both_patterns():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_PORT": "8080"}
    result = filter_env(env, key_pattern=r"PORT", value_pattern=r"^\d+$")
    assert result == {"DB_PORT": "5432", "APP_PORT": "8080"}


def test_filter_no_patterns_returns_all():
    env = {"A": "1", "B": "2"}
    assert filter_env(env) == env


def test_filter_invert_excludes_matching_keys():
    env = {"SECRET_KEY": "abc", "APP_NAME": "myapp", "SECRET_TOKEN": "xyz"}
    result = filter_env(env, key_pattern=r"^SECRET_", invert=True)
    assert result == {"APP_NAME": "myapp"}


def test_filter_invert_value_pattern():
    env = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
    result = filter_env(env, value_pattern=r"^\d+$", invert=True)
    assert "PORT" not in result
    assert "HOST" in result and "DEBUG" in result


def test_filter_empty_env_returns_empty():
    assert filter_env({}, key_pattern=r"DB") == {}


def test_filter_pattern_no_matches_returns_empty():
    env = {"APP_NAME": "myapp"}
    result = filter_env(env, key_pattern=r"^DB_")
    assert result == {}


# ---------------------------------------------------------------------------
# filter_envs integration tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def test_filter_envs_changed_flag(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "DB_HOST=localhost\nDB_PORT=5432\nAPP_NAME=myapp\n")
    results = filter_envs([f], key_pattern=r"^DB_")
    assert len(results) == 1
    r = results[0]
    assert r.changed is True
    assert "APP_NAME" in r.removed_keys
    assert r.filtered == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_filter_envs_unchanged_when_all_match(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    results = filter_envs([f], key_pattern=r"^DB_")
    assert results[0].changed is False
    assert results[0].removed_keys == []


def test_filter_envs_multiple_files(tmp_dir: Path):
    f1 = _write(tmp_dir / ".env.a", "SECRET=abc\nPORT=8080\n")
    f2 = _write(tmp_dir / ".env.b", "SECRET=xyz\nHOST=example.com\n")
    results = filter_envs([f1, f2], key_pattern=r"^SECRET$")
    assert results[0].filtered == {"SECRET": "abc"}
    assert results[1].filtered == {"SECRET": "xyz"}


# ---------------------------------------------------------------------------
# format_filter_report
# ---------------------------------------------------------------------------

def test_format_filter_report_includes_removed_keys(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "DB_HOST=localhost\nAPP_NAME=myapp\n")
    results = filter_envs([f], key_pattern=r"^DB_")
    report = format_filter_report(results)
    assert "removed: APP_NAME" in report
    assert "changed" in report


def test_format_filter_report_unchanged(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "DB_HOST=localhost\n")
    results = filter_envs([f], key_pattern=r"^DB_")
    report = format_filter_report(results)
    assert "unchanged" in report
