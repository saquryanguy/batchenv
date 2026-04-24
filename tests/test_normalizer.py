"""Tests for batchenv.normalizer."""
from __future__ import annotations

import pytest

from batchenv.normalizer import (
    NormalizeResult,
    _normalize_key,
    normalize_env,
    normalize_envs,
    format_normalize_report,
)


# ---------------------------------------------------------------------------
# _normalize_key
# ---------------------------------------------------------------------------

def test_normalize_key_uppercase():
    assert _normalize_key("db_host") == "DB_HOST"


def test_normalize_key_replaces_hyphens():
    assert _normalize_key("my-key") == "MY_KEY"


def test_normalize_key_strips_whitespace():
    assert _normalize_key("  PORT  ") == "PORT"


def test_normalize_key_already_normal():
    assert _normalize_key("DB_HOST") == "DB_HOST"


def test_normalize_key_combined():
    assert _normalize_key(" api-secret-key ") == "API_SECRET_KEY"


# ---------------------------------------------------------------------------
# normalize_env
# ---------------------------------------------------------------------------

def test_normalize_env_no_changes():
    env = {"DB_HOST": "localhost", "PORT": "5432"}
    result = normalize_env("a.env", env)
    assert not result.changed
    assert result.changes == []
    assert result.normalized == env


def test_normalize_env_detects_changes():
    env = {"db_host": "localhost", "PORT": "5432"}
    result = normalize_env("a.env", env)
    assert result.changed
    assert ("db_host", "DB_HOST") in result.changes
    assert result.normalized["DB_HOST"] == "localhost"
    assert result.normalized["PORT"] == "5432"


def test_normalize_env_hyphen_key():
    env = {"my-token": "abc123"}
    result = normalize_env("b.env", env)
    assert result.normalized == {"MY_TOKEN": "abc123"}
    assert result.changes == [("my-token", "MY_TOKEN")]


def test_normalize_env_collision_last_wins():
    # Both 'db_host' and 'DB_HOST' normalize to 'DB_HOST'; last value wins.
    env = {"db_host": "first", "DB_HOST": "second"}
    result = normalize_env("c.env", env)
    assert result.normalized["DB_HOST"] == "second"


def test_normalize_env_preserves_values():
    env = {"secret-key": "s3cr3t!"}
    result = normalize_env("d.env", env)
    assert result.normalized["SECRET_KEY"] == "s3cr3t!"


# ---------------------------------------------------------------------------
# normalize_envs
# ---------------------------------------------------------------------------

def test_normalize_envs_multiple_files():
    envs = {
        "a.env": {"db_host": "localhost"},
        "b.env": {"DB_HOST": "prod-server"},
    }
    results = normalize_envs(envs)
    assert results["a.env"].changed
    assert not results["b.env"].changed


# ---------------------------------------------------------------------------
# format_normalize_report
# ---------------------------------------------------------------------------

def test_format_normalize_report_with_changes():
    env = {"db_host": "localhost"}
    results = {"a.env": normalize_env("a.env", env)}
    report = format_normalize_report(results)
    assert "a.env" in report
    assert "db_host" in report
    assert "DB_HOST" in report


def test_format_normalize_report_no_changes():
    env = {"DB_HOST": "localhost"}
    results = {"a.env": normalize_env("a.env", env)}
    report = format_normalize_report(results)
    assert "no changes" in report
