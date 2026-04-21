"""Tests for batchenv.grouper."""
import pytest
from batchenv.grouper import (
    GroupResult,
    group_env,
    group_envs,
    format_group_report,
)


def test_basic_grouping():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_NAME": "myapp", "APP_ENV": "prod"}
    result = group_env(env)
    assert "DB" in result.groups
    assert "APP" in result.groups
    assert len(result.groups["DB"]) == 2
    assert len(result.groups["APP"]) == 2
    assert result.ungrouped == []
    assert result.changed is True


def test_ungrouped_keys():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "STANDALONE": "yes"}
    result = group_env(env)
    assert "DB" in result.groups
    assert any(k == "STANDALONE" for k, _ in result.ungrouped)


def test_min_group_size_respected():
    env = {"DB_HOST": "localhost", "APP_NAME": "myapp"}
    result = group_env(env, min_group_size=2)
    assert result.groups == {}
    assert len(result.ungrouped) == 2
    assert result.changed is False


def test_custom_separator():
    env = {"DB.HOST": "localhost", "DB.PORT": "5432", "OTHER": "val"}
    result = group_env(env, separator=".")
    assert "DB" in result.groups
    assert any(k == "OTHER" for k, _ in result.ungrouped)


def test_empty_env():
    result = group_env({})
    assert result.groups == {}
    assert result.ungrouped == []
    assert result.changed is False


def test_no_separator_in_keys():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = group_env(env)
    assert result.groups == {}
    assert len(result.ungrouped) == 2


def test_group_envs_multiple_files():
    envs = {
        "a.env": {"DB_HOST": "h", "DB_PORT": "p"},
        "b.env": {"CACHE_URL": "redis", "CACHE_TTL": "60"},
    }
    results = group_envs(envs)
    assert "DB" in results["a.env"].groups
    assert "CACHE" in results["b.env"].groups


def test_format_group_report_with_groups():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = group_env(env)
    report = format_group_report("test.env", result)
    assert "test.env:" in report
    assert "[DB]" in report
    assert "DB_HOST" in report
    assert "DB_PORT" in report


def test_format_group_report_no_groups():
    result = group_env({})
    report = format_group_report("empty.env", result)
    assert "no groups found" in report


def test_format_group_report_ungrouped():
    env = {"DB_HOST": "h", "DB_PORT": "p", "SOLO": "val"}
    result = group_env(env)
    report = format_group_report("test.env", result)
    assert "[ungrouped]" in report
    assert "SOLO" in report
