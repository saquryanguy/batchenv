"""Tests for batchenv.injector."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from batchenv.injector import inject_env, format_inject_report


@pytest.fixture()
def tmp_env(tmp_path: Path):
    """Write a simple .env file and return its path."""

    def _write(content: str) -> Path:
        p = tmp_path / ".env"
        p.write_text(content)
        return p

    return _write


def test_inject_adds_new_key(tmp_env, monkeypatch):
    monkeypatch.delenv("_BATCHENV_TEST_KEY", raising=False)
    path = tmp_env("_BATCHENV_TEST_KEY=hello\n")
    result = inject_env(path)
    assert "_BATCHENV_TEST_KEY" in result.injected
    assert os.environ["_BATCHENV_TEST_KEY"] == "hello"
    assert result.changed is True


def test_inject_skips_existing_without_overwrite(tmp_env, monkeypatch):
    monkeypatch.setenv("_BATCHENV_EXISTING", "original")
    path = tmp_env("_BATCHENV_EXISTING=new\n")
    result = inject_env(path, overwrite=False)
    assert "_BATCHENV_EXISTING" in result.skipped
    assert os.environ["_BATCHENV_EXISTING"] == "original"
    assert result.changed is False


def test_inject_overwrites_when_flag_set(tmp_env, monkeypatch):
    monkeypatch.setenv("_BATCHENV_OW", "old")
    path = tmp_env("_BATCHENV_OW=new\n")
    result = inject_env(path, overwrite=True)
    assert "_BATCHENV_OW" in result.overwritten
    assert os.environ["_BATCHENV_OW"] == "new"
    assert result.changed is True


def test_inject_dry_run_does_not_modify(tmp_env, monkeypatch):
    monkeypatch.delenv("_BATCHENV_DRY", raising=False)
    path = tmp_env("_BATCHENV_DRY=value\n")
    result = inject_env(path, dry_run=True)
    assert "_BATCHENV_DRY" in result.injected
    assert "_BATCHENV_DRY" not in os.environ
    assert result.changed is True


def test_inject_key_allowlist(tmp_env, monkeypatch):
    monkeypatch.delenv("_BATCHENV_A", raising=False)
    monkeypatch.delenv("_BATCHENV_B", raising=False)
    path = tmp_env("_BATCHENV_A=1\n_BATCHENV_B=2\n")
    result = inject_env(path, keys=["_BATCHENV_A"])
    assert "_BATCHENV_A" in result.injected
    assert "_BATCHENV_B" not in result.injected
    assert "_BATCHENV_B" not in os.environ


def test_format_inject_report_shows_all_categories(tmp_env, monkeypatch):
    monkeypatch.delenv("_BATCHENV_NEW", raising=False)
    monkeypatch.setenv("_BATCHENV_SKIP", "keep")
    monkeypatch.setenv("_BATCHENV_OVER", "old")
    path = tmp_env("_BATCHENV_NEW=x\n_BATCHENV_SKIP=y\n_BATCHENV_OVER=z\n")
    result = inject_env(path, overwrite=True)
    report = format_inject_report([result])
    assert "(injected)" in report
    assert "(skipped" in report or "(overwritten)" in report
    assert str(path) in report


def test_format_inject_report_empty_env(tmp_env):
    path = tmp_env("")
    result = inject_env(path)
    report = format_inject_report([result])
    assert "(no variables)" in report
