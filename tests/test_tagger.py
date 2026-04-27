"""Tests for batchenv.tagger."""
from __future__ import annotations

import pytest

from batchenv.tagger import (
    TagResult,
    _strip_existing_tag,
    format_tag_report,
    tag_env,
    tag_envs,
)


def test_strip_existing_tag_removes_comment():
    assert _strip_existing_tag("localhost  # dev") == "localhost"


def test_strip_existing_tag_no_comment():
    assert _strip_existing_tag("localhost") == "localhost"


def test_tag_env_basic():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = tag_env("a.env", env, {"DB_HOST": "database host"})
    assert result.tagged["DB_HOST"] == "localhost  # database host"
    assert result.tagged["DB_PORT"] == "5432"
    assert result.keys_tagged == ["DB_HOST"]
    assert result.changed is True


def test_tag_env_skips_missing_keys():
    env = {"APP_NAME": "myapp"}
    result = tag_env("a.env", env, {"MISSING_KEY": "some tag"})
    assert result.tagged == {"APP_NAME": "myapp"}
    assert result.keys_tagged == []
    assert result.changed is False


def test_tag_env_skips_existing_comment_without_overwrite():
    env = {"API_KEY": "abc123  # secret"}
    result = tag_env("a.env", env, {"API_KEY": "new tag"}, overwrite=False)
    assert result.tagged["API_KEY"] == "abc123  # secret"
    assert result.keys_tagged == []
    assert result.changed is False


def test_tag_env_overwrites_existing_comment_when_flag_set():
    env = {"API_KEY": "abc123  # old tag"}
    result = tag_env("a.env", env, {"API_KEY": "new tag"}, overwrite=True)
    assert result.tagged["API_KEY"] == "abc123  # new tag"
    assert result.keys_tagged == ["API_KEY"]
    assert result.changed is True


def test_tag_env_does_not_mutate_original():
    env = {"X": "1"}
    tag_env("a.env", env, {"X": "tagged"})
    assert env["X"] == "1"


def test_tag_envs_multiple_files():
    envs = [
        ("a.env", {"HOST": "localhost"}),
        ("b.env", {"HOST": "remotehost"}),
    ]
    results = tag_envs(envs, {"HOST": "server"})
    assert len(results) == 2
    assert all(r.changed for r in results)
    assert results[0].tagged["HOST"] == "localhost  # server"
    assert results[1].tagged["HOST"] == "remotehost  # server"


def test_format_tag_report_changed():
    env = {"DB": "pg"}
    result = tag_env("x.env", env, {"DB": "primary db"})
    report = format_tag_report([result])
    assert "x.env: changed" in report
    assert "+ DB" in report
    assert "primary db" in report


def test_format_tag_report_unchanged():
    env = {"APP": "web"}
    result = tag_env("x.env", env, {"NOPE": "tag"})
    report = format_tag_report([result])
    assert "x.env: unchanged" in report
