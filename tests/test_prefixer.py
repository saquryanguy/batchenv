"""Tests for batchenv.prefixer."""
from pathlib import Path

import pytest

from batchenv.prefixer import (
    PrefixResult,
    format_prefix_report,
    prefix_env,
    prefix_envs,
)


# ---------------------------------------------------------------------------
# Unit tests for prefix_env
# ---------------------------------------------------------------------------

def test_prefix_env_basic():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = prefix_env(env, "APP_")
    assert result.prefixed == {"APP_HOST": "localhost", "APP_PORT": "5432"}
    assert result.changed is True
    assert result.skipped_keys == []


def test_prefix_env_already_prefixed_skipped_by_default():
    env = {"APP_HOST": "localhost", "PORT": "5432"}
    result = prefix_env(env, "APP_")
    assert "APP_HOST" in result.prefixed
    assert "APP_PORT" in result.prefixed
    assert result.skipped_keys == ["APP_HOST"]


def test_prefix_env_already_prefixed_not_skipped_when_flag_false():
    env = {"APP_HOST": "localhost"}
    result = prefix_env(env, "APP_", skip_already_prefixed=False)
    assert "APP_APP_HOST" in result.prefixed
    assert result.skipped_keys == []


def test_prefix_env_empty_env():
    result = prefix_env({}, "X_")
    assert result.prefixed == {}
    assert result.changed is False


def test_prefix_env_empty_prefix():
    env = {"KEY": "value"}
    result = prefix_env(env, "")
    # Empty prefix: keys unchanged, skip_already_prefixed would match everything
    assert result.prefixed == {"KEY": "value"}
    assert result.changed is False


def test_prefix_env_does_not_mutate_original():
    env = {"A": "1"}
    prefix_env(env, "PRE_")
    assert env == {"A": "1"}


def test_prefix_env_preserves_values():
    env = {"SECRET": "s3cr3t", "URL": "http://example.com"}
    result = prefix_env(env, "SVC_")
    assert result.prefixed["SVC_SECRET"] == "s3cr3t"
    assert result.prefixed["SVC_URL"] == "http://example.com"


# ---------------------------------------------------------------------------
# Integration tests using temporary files
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> None:
    path.write_text(content)


def test_prefix_envs_multiple_files(tmp_dir: Path):
    f1 = tmp_dir / ".env.a"
    f2 = tmp_dir / ".env.b"
    _write(f1, "HOST=localhost\nPORT=8080\n")
    _write(f2, "DB_NAME=mydb\n")

    results = prefix_envs([f1, f2], "SVC_")
    assert len(results) == 2
    assert results[0].prefixed == {"SVC_HOST": "localhost", "SVC_PORT": "8080"}
    assert results[1].prefixed == {"SVC_DB_NAME": "mydb"}


def test_prefix_envs_unchanged_file(tmp_dir: Path):
    f = tmp_dir / ".env"
    _write(f, "SVC_KEY=value\n")
    results = prefix_envs([f], "SVC_")
    assert results[0].changed is False


# ---------------------------------------------------------------------------
# format_prefix_report
# ---------------------------------------------------------------------------

def test_format_prefix_report_changed():
    r = PrefixResult(
        path=Path("/app/.env"),
        original={"KEY": "val"},
        prefixed={"APP_KEY": "val"},
        changed=True,
    )
    report = format_prefix_report([r])
    assert "/app/.env" in report
    assert "changed" in report


def test_format_prefix_report_skipped_keys():
    r = PrefixResult(
        path=Path("/app/.env"),
        original={"APP_KEY": "val"},
        prefixed={"APP_KEY": "val"},
        changed=False,
        skipped_keys=["APP_KEY"],
    )
    report = format_prefix_report([r])
    assert "APP_KEY" in report
    assert "skipped" in report
