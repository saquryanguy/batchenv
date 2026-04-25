"""Tests for batchenv.scoper."""
from __future__ import annotations

import pytest

from batchenv.scoper import (
    ScopeResult,
    format_scope_report,
    scope_env,
    scope_envs,
)


ENV = {
    "APP_HOST": "localhost",
    "APP_PORT": "8080",
    "DB_HOST": "db.local",
    "DB_PORT": "5432",
    "DEBUG": "true",
}


def test_scope_by_prefix_keeps_matching_keys():
    result = scope_env(ENV, "app.env", prefix="APP_")
    assert set(result.filtered.keys()) == {"APP_HOST", "APP_PORT"}


def test_scope_by_prefix_removes_non_matching_keys():
    result = scope_env(ENV, "app.env", prefix="APP_")
    assert "DB_HOST" in result.removed_keys
    assert "DEBUG" in result.removed_keys


def test_scope_strip_prefix_renames_keys():
    result = scope_env(ENV, "app.env", prefix="APP_", strip_prefix=True)
    assert "HOST" in result.filtered
    assert "PORT" in result.filtered
    assert "APP_HOST" not in result.filtered


def test_scope_strip_prefix_preserves_values():
    result = scope_env(ENV, "app.env", prefix="APP_", strip_prefix=True)
    assert result.filtered["HOST"] == "localhost"
    assert result.filtered["PORT"] == "8080"


def test_scope_by_pattern():
    result = scope_env(ENV, "app.env", pattern=r"_PORT$")
    assert set(result.filtered.keys()) == {"APP_PORT", "DB_PORT"}


def test_scope_prefix_and_pattern_union():
    result = scope_env(ENV, "app.env", prefix="DEBUG", pattern=r"^DB_")
    assert "DEBUG" in result.filtered
    assert "DB_HOST" in result.filtered
    assert "DB_PORT" in result.filtered
    assert "APP_HOST" not in result.filtered


def test_scope_no_prefix_or_pattern_raises():
    with pytest.raises(ValueError, match="At least one"):
        scope_env(ENV, "app.env")


def test_scope_changed_flag_true_when_keys_removed():
    result = scope_env(ENV, "app.env", prefix="APP_")
    assert result.changed is True


def test_scope_changed_flag_false_when_all_match():
    small_env = {"APP_A": "1", "APP_B": "2"}
    result = scope_env(small_env, "app.env", prefix="APP_")
    assert result.changed is False
    assert result.removed_keys == []


def test_scope_envs_multiple_files():
    envs = {
        "a.env": {"APP_X": "1", "OTHER": "2"},
        "b.env": {"APP_Y": "3", "EXTRA": "4"},
    }
    results = scope_envs(envs, prefix="APP_")
    assert len(results) == 2
    assert all(isinstance(r, ScopeResult) for r in results)
    paths = {r.path for r in results}
    assert paths == {"a.env", "b.env"}


def test_format_scope_report_includes_path_and_counts():
    result = scope_env(ENV, "app.env", prefix="APP_")
    report = format_scope_report([result])
    assert "app.env" in report
    assert "2 kept" in report
    assert "3 removed" in report


def test_format_scope_report_lists_removed_keys():
    result = scope_env(ENV, "app.env", prefix="APP_")
    report = format_scope_report([result])
    assert "DB_HOST" in report
    assert "DEBUG" in report
