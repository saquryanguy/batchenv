"""Tests for batchenv.diff module."""

import pytest
from batchenv.diff import diff_envs, format_diff, EnvDiff


SOURCE = {
    "APP_NAME": "myapp",
    "DEBUG": "true",
    "SECRET": "abc123",
    "ONLY_SRC": "yes",
}

TARGET = {
    "APP_NAME": "myapp",
    "DEBUG": "false",
    "DB_URL": "postgres://localhost/db",
    "ONLY_SRC": None,
}


def test_only_in_source():
    result = diff_envs(SOURCE, TARGET)
    assert "SECRET" in result.only_in_source
    assert result.only_in_source["SECRET"] == "abc123"


def test_only_in_target():
    result = diff_envs(SOURCE, TARGET)
    assert "DB_URL" in result.only_in_target


def test_value_changed():
    result = diff_envs(SOURCE, TARGET)
    assert "DEBUG" in result.value_changed
    assert result.value_changed["DEBUG"] == ("true", "false")


def test_matching_keys():
    result = diff_envs(SOURCE, TARGET)
    assert "APP_NAME" in result.matching


def test_has_differences_true():
    result = diff_envs(SOURCE, TARGET)
    assert result.has_differences is True


def test_has_differences_false():
    same = {"KEY": "val"}
    result = diff_envs(same, same)
    assert result.has_differences is False


def test_identical_envs_all_matching():
    env = {"A": "1", "B": "2"}
    result = diff_envs(env, env)
    assert result.matching == {"A", "B"}
    assert not result.only_in_source
    assert not result.only_in_target
    assert not result.value_changed


def test_format_diff_no_differences():
    env = {"X": "1"}
    diff = diff_envs(env, env)
    lines = format_diff(diff)
    assert lines == ["No differences found."]


def test_format_diff_labels():
    diff = diff_envs({"A": "1"}, {"B": "2"})
    lines = format_diff(diff, source_label="prod", target_label="local")
    assert any("prod only" in l for l in lines)
    assert any("local only" in l for l in lines)


def test_empty_dicts():
    result = diff_envs({}, {})
    assert not result.has_differences
    assert result.matching == set()
