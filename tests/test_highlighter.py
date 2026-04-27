"""Tests for batchenv.highlighter."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from batchenv.highlighter import (
    HighlightResult,
    format_highlight_report,
    highlight_env,
    highlight_envs,
)


# ---------------------------------------------------------------------------
# Unit tests for highlight_env
# ---------------------------------------------------------------------------

def test_highlight_adds_marker_to_key():
    env = {"DB_HOST": "localhost", "APP_ENV": "dev"}
    result = highlight_env(env, keys=["DB_HOST"])
    assert "# [highlighted]" in result["DB_HOST"]
    assert result["APP_ENV"] == "dev"


def test_highlight_does_not_duplicate_marker_by_default():
    env = {"KEY": "value # [highlighted]"}
    result = highlight_env(env, keys=["KEY"], overwrite=False)
    # Marker already present — should not be added again
    assert result["KEY"].count("# [highlighted]") == 1


def test_highlight_overwrites_when_flag_set():
    env = {"KEY": "value # [highlighted]"}
    result = highlight_env(env, keys=["KEY"], overwrite=True)
    assert result["KEY"].count("# [highlighted]") == 1
    assert result["KEY"].startswith("value")


def test_highlight_custom_marker():
    env = {"SECRET": "abc123"}
    result = highlight_env(env, keys=["SECRET"], marker="# REVIEW")
    assert "# REVIEW" in result["SECRET"]


def test_highlight_skips_absent_keys():
    env = {"A": "1", "B": "2"}
    result = highlight_env(env, keys=["C"])
    assert result == env


def test_highlight_empty_env():
    result = highlight_env({}, keys=["KEY"])
    assert result == {}


# ---------------------------------------------------------------------------
# Integration tests using real files
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> str:
    path.write_text(content)
    return str(path)


def test_highlight_envs_marks_file(tmp_dir: Path):
    p = _write(tmp_dir / ".env", "DB_HOST=localhost\nAPP_ENV=dev\n")
    results = highlight_envs([p], keys=["DB_HOST"])
    assert len(results) == 1
    r = results[0]
    assert r.changed is True
    assert "DB_HOST" in r.marked_keys
    assert "# [highlighted]" in r.highlighted["DB_HOST"]


def test_highlight_envs_unchanged_when_no_matching_keys(tmp_dir: Path):
    p = _write(tmp_dir / ".env", "FOO=bar\n")
    results = highlight_envs([p], keys=["MISSING"])
    assert results[0].changed is False


def test_format_highlight_report_changed(tmp_dir: Path):
    p = _write(tmp_dir / ".env", "TOKEN=abc\n")
    results = highlight_envs([p], keys=["TOKEN"])
    report = format_highlight_report(results)
    assert "changed" in report
    assert "TOKEN" in report


def test_format_highlight_report_unchanged(tmp_dir: Path):
    p = _write(tmp_dir / ".env", "FOO=bar\n")
    results = highlight_envs([p], keys=["MISSING"])
    report = format_highlight_report(results)
    assert "unchanged" in report
