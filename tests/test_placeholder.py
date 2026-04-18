import pytest
from batchenv.placeholder import (
    fill_placeholders,
    fill_envs,
    format_placeholder_report,
    PlaceholderResult,
)


def test_fills_empty_value():
    env = {"KEY": ""}
    result, filled, skipped = fill_placeholders(env, {"KEY": "newval"})
    assert result["KEY"] == "newval"
    assert "KEY" in filled
    assert skipped == []


def test_fills_placeholder_value():
    env = {"KEY": "PLACEHOLDER"}
    result, filled, skipped = fill_placeholders(env, {"KEY": "real"})
    assert result["KEY"] == "real"
    assert "KEY" in filled


def test_skips_existing_value():
    env = {"KEY": "existing"}
    result, filled, skipped = fill_placeholders(env, {"KEY": "new"})
    assert result["KEY"] == "existing"
    assert "KEY" in skipped
    assert filled == {}


def test_overwrite_flag():
    env = {"KEY": "existing"}
    result, filled, skipped = fill_placeholders(env, {"KEY": "new"}, overwrite=True)
    assert result["KEY"] == "new"
    assert "KEY" in filled


def test_skips_missing_key():
    env = {"OTHER": "val"}
    result, filled, skipped = fill_placeholders(env, {"MISSING": "x"})
    assert "MISSING" not in result
    assert "MISSING" in skipped


def test_fill_envs_multiple():
    envs = {
        "a/.env": {"A": "", "B": "keep"},
        "b/.env": {"A": "PLACEHOLDER"},
    }
    results = fill_envs(envs, {"A": "filled"})
    assert len(results) == 2
    assert results[0].changed is True
    assert results[0].filled == {"A": "filled"}
    assert results[1].changed is True


def test_fill_envs_no_change():
    envs = {"a/.env": {"KEY": "value"}}
    results = fill_envs(envs, {"KEY": "other"})
    assert results[0].changed is False


def test_format_report():
    results = [
        PlaceholderResult(path="a/.env", filled={"K": "v"}, skipped=["S"], changed=True)
    ]
    report = format_placeholder_report(results)
    assert "a/.env: changed" in report
    assert "filled: K=v" in report
    assert "skipped: S" in report
