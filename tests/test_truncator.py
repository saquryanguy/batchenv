"""Tests for batchenv.truncator."""
import pytest

from batchenv.truncator import (
    TruncateResult,
    format_truncate_report,
    truncate_env,
    truncate_envs,
)


def test_truncate_basic_value():
    env = {"KEY": "hello_world"}
    result = truncate_env(env, max_length=8)
    assert result.truncated["KEY"] == "hello..."
    assert "KEY" in result.affected_keys
    assert result.changed is True


def test_truncate_value_exactly_at_limit_is_not_truncated():
    env = {"KEY": "12345"}
    result = truncate_env(env, max_length=5)
    assert result.truncated["KEY"] == "12345"
    assert result.affected_keys == []
    assert result.changed is False


def test_truncate_short_value_unchanged():
    env = {"KEY": "hi"}
    result = truncate_env(env, max_length=10)
    assert result.truncated["KEY"] == "hi"
    assert result.changed is False


def test_truncate_empty_value_unchanged():
    env = {"KEY": ""}
    result = truncate_env(env, max_length=5)
    assert result.truncated["KEY"] == ""
    assert result.changed is False


def test_truncate_custom_suffix():
    env = {"KEY": "abcdefgh"}
    result = truncate_env(env, max_length=6, suffix="--")
    assert result.truncated["KEY"] == "abcd--"
    assert len(result.truncated["KEY"]) == 6


def test_truncate_scoped_to_keys_only():
    env = {"A": "longvalue123", "B": "longvalue456"}
    result = truncate_env(env, max_length=8, keys=["A"])
    assert result.truncated["A"] == "longi..."
    assert result.truncated["B"] == "longvalue456"  # untouched
    assert result.affected_keys == ["A"]


def test_truncate_does_not_mutate_original():
    env = {"KEY": "verylongvalue"}
    original_copy = dict(env)
    truncate_env(env, max_length=5)
    assert env == original_copy


def test_truncate_invalid_max_length_raises():
    with pytest.raises(ValueError, match="max_length"):
        truncate_env({"K": "v"}, max_length=2, suffix="...")


def test_truncate_envs_multiple_files():
    envs = {
        ".env.dev": {"SECRET": "short", "TOKEN": "averylongtokenvalue"},
        ".env.prod": {"SECRET": "anotherlongone", "TOKEN": "ok"},
    }
    results = truncate_envs(envs, max_length=10)
    assert len(results) == 2
    dev = next(r for r in results if r.path == ".env.dev")
    prod = next(r for r in results if r.path == ".env.prod")
    assert "TOKEN" in dev.affected_keys
    assert "SECRET" not in dev.affected_keys
    assert "SECRET" in prod.affected_keys
    assert "TOKEN" not in prod.affected_keys


def test_format_truncate_report_changed():
    result = TruncateResult(
        path=".env",
        original={"A": "longvalue"},
        truncated={"A": "lon..."},
        affected_keys=["A"],
    )
    report = format_truncate_report([result])
    assert ".env" in report
    assert "1 key(s)" in report
    assert "A" in report


def test_format_truncate_report_no_change():
    result = TruncateResult(
        path=".env",
        original={"A": "hi"},
        truncated={"A": "hi"},
        affected_keys=[],
    )
    report = format_truncate_report([result])
    assert "no values truncated" in report
