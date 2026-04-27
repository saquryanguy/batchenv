"""Tests for batchenv.masker."""
from __future__ import annotations

import pytest

from batchenv.masker import (
    DEFAULT_MASK,
    MaskResult,
    format_mask_report,
    mask_env,
    mask_envs,
)


def test_mask_all_keys_by_default():
    env = {"DB_PASSWORD": "secret", "API_KEY": "abc123", "HOST": "localhost"}
    result = mask_env(env, "test.env")
    assert result.masked["DB_PASSWORD"] == DEFAULT_MASK
    assert result.masked["API_KEY"] == DEFAULT_MASK
    assert result.masked["HOST"] == DEFAULT_MASK
    assert set(result.keys_masked) == {"DB_PASSWORD", "API_KEY", "HOST"}
    assert result.changed is True


def test_mask_specific_keys_only():
    env = {"DB_PASSWORD": "secret", "HOST": "localhost"}
    result = mask_env(env, "test.env", keys=["DB_PASSWORD"])
    assert result.masked["DB_PASSWORD"] == DEFAULT_MASK
    assert result.masked["HOST"] == "localhost"
    assert result.keys_masked == ["DB_PASSWORD"]


def test_mask_skips_empty_values():
    env = {"EMPTY": "", "PRESENT": "value"}
    result = mask_env(env, "test.env")
    assert result.masked["EMPTY"] == ""
    assert result.masked["PRESENT"] == DEFAULT_MASK
    assert "EMPTY" not in result.keys_masked


def test_mask_custom_placeholder():
    env = {"TOKEN": "supersecret"}
    result = mask_env(env, "test.env", mask="[REDACTED]")
    assert result.masked["TOKEN"] == "[REDACTED]"


def test_mask_visible_chars_suffix():
    env = {"TOKEN": "abcdefgh"}
    result = mask_env(env, "test.env", visible_chars=3)
    assert result.masked["TOKEN"] == DEFAULT_MASK + "fgh"


def test_mask_visible_chars_value_too_short():
    """When value is shorter than visible_chars, use plain mask."""
    env = {"TOKEN": "ab"}
    result = mask_env(env, "test.env", visible_chars=5)
    assert result.masked["TOKEN"] == DEFAULT_MASK


def test_mask_key_not_in_env():
    """Requesting a key not present in env silently skips it."""
    env = {"HOST": "localhost"}
    result = mask_env(env, "test.env", keys=["MISSING_KEY"])
    assert result.masked["HOST"] == "localhost"
    assert result.keys_masked == []
    assert result.changed is False


def test_mask_original_is_not_mutated():
    env = {"SECRET": "value"}
    original_copy = dict(env)
    mask_env(env, "test.env")
    assert env == original_copy


def test_mask_envs_multiple_files():
    envs = {
        "a.env": {"KEY": "val1"},
        "b.env": {"KEY": "val2"},
    }
    results = mask_envs(envs, keys=["KEY"])
    assert len(results) == 2
    assert all(r.masked["KEY"] == DEFAULT_MASK for r in results)


def test_mask_envs_preserves_path():
    """Each MaskResult returned by mask_envs should carry the correct file path."""
    envs = {
        "first.env": {"TOKEN": "abc"},
        "second.env": {"TOKEN": "xyz"},
    }
    results = mask_envs(envs, keys=["TOKEN"])
    paths = {r.path for r in results}
    assert paths == {"first.env", "second.env"}


def test_format_mask_report_with_changes():
    env = {"SECRET": "x"}
    result = mask_env(env, "prod.env")
    report = format_mask_report([result])
    assert "prod.env" in report
    assert "1 key(s) masked" in report
    assert "SECRET" in report


def test_format_mask_report_no_changes():
    result = MaskResult(path="empty.env", original={}, masked={}, keys_masked=[], changed=False)
    report = format_mask_report([result])
    assert "no ch
