"""Tests for batchenv.comparator."""
import pytest
from batchenv.comparator import compare_envs, format_compare_report


ENV_A = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}
ENV_B = {"DB_HOST": "prod.db", "DB_PORT": "5432", "API_KEY": "xyz"}
ENV_C = {"DB_HOST": "staging.db", "SECRET": "abc", "EXTRA": "1"}


def test_all_keys_collected():
    result = compare_envs({"a": ENV_A, "b": ENV_B})
    assert set(result.all_keys) == {"DB_HOST", "DB_PORT", "SECRET", "API_KEY"}


def test_common_keys_both_present():
    result = compare_envs({"a": ENV_A, "b": ENV_B})
    assert result.common_keys == {"DB_HOST", "DB_PORT"}


def test_unique_keys_partial_presence():
    result = compare_envs({"a": ENV_A, "b": ENV_B})
    assert "SECRET" in result.unique_keys
    assert result.unique_keys["SECRET"] == {"a"}
    assert "API_KEY" in result.unique_keys
    assert result.unique_keys["API_KEY"] == {"b"}


def test_matrix_values_correct():
    result = compare_envs({"a": ENV_A, "b": ENV_B})
    assert result.matrix["DB_HOST"]["a"] == "localhost"
    assert result.matrix["DB_HOST"]["b"] == "prod.db"
    assert result.matrix["SECRET"]["b"] is None


def test_three_files_common_key():
    result = compare_envs({"a": ENV_A, "b": ENV_B, "c": ENV_C})
    assert "DB_HOST" in result.common_keys
    assert "SECRET" not in result.common_keys  # missing in b


def test_empty_envs():
    result = compare_envs({})
    assert result.files == []
    assert result.all_keys == []
    assert result.common_keys == set()


def test_single_file():
    result = compare_envs({"a": ENV_A})
    assert result.common_keys == set(ENV_A.keys())
    assert result.unique_keys == {}


def test_identical_files():
    result = compare_envs({"a": ENV_A, "b": ENV_A})
    assert result.common_keys == set(ENV_A.keys())
    assert result.unique_keys == {}


def test_format_report_contains_keys():
    result = compare_envs({"a": ENV_A, "b": ENV_B})
    report = format_compare_report(result)
    assert "DB_HOST" in report
    assert "<missing>" in report
    assert "Common keys" in report
    assert "Partial keys" in report


def test_format_report_empty():
    result = compare_envs({})
    report = format_compare_report(result)
    assert report == "No files to compare."


def test_keys_are_sorted():
    result = compare_envs({"a": {"ZEBRA": "1", "ALPHA": "2"}})
    assert result.all_keys == ["ALPHA", "ZEBRA"]
