"""Tests for batchenv.patcher."""
from pathlib import Path

import pytest

from batchenv.patcher import patch_env, patch_envs, format_patch_report


# ---------------------------------------------------------------------------
# patch_env unit tests
# ---------------------------------------------------------------------------

def test_patch_adds_new_key():
    env = {"A": "1"}
    updated, applied, skipped = patch_env(env, {"B": "2"})
    assert updated["B"] == "2"
    assert "B" in applied
    assert skipped == []


def test_patch_overwrites_existing_key_by_default():
    env = {"A": "old"}
    updated, applied, skipped = patch_env(env, {"A": "new"})
    assert updated["A"] == "new"
    assert "A" in applied
    assert skipped == []


def test_patch_skips_existing_key_when_no_overwrite():
    env = {"A": "old"}
    updated, applied, skipped = patch_env(env, {"A": "new"}, overwrite=False)
    assert updated["A"] == "old"
    assert applied == []
    assert "A" in skipped


def test_patch_adds_new_key_even_when_no_overwrite():
    env = {"A": "1"}
    updated, applied, skipped = patch_env(env, {"B": "2"}, overwrite=False)
    assert updated["B"] == "2"
    assert "B" in applied


def test_patch_does_not_mutate_original():
    env = {"A": "1"}
    patch_env(env, {"A": "2"})
    assert env["A"] == "1"


# ---------------------------------------------------------------------------
# patch_envs integration tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_patch_envs_writes_file(tmp_dir: Path):
    f = tmp_dir / ".env"
    _write(f, "A=1\n")
    results = patch_envs([f], {"B": "2"})
    assert results[0].changed is True
    assert "B=2" in f.read_text()


def test_patch_envs_dry_run_does_not_modify(tmp_dir: Path):
    f = tmp_dir / ".env"
    _write(f, "A=1\n")
    patch_envs([f], {"B": "2"}, dry_run=True)
    assert "B" not in f.read_text()


def test_patch_envs_no_overwrite_skips(tmp_dir: Path):
    f = tmp_dir / ".env"
    _write(f, "A=original\n")
    results = patch_envs([f], {"A": "replaced"}, overwrite=False)
    assert results[0].skipped == ["A"]
    assert "original" in f.read_text()


def test_patch_envs_missing_file_created(tmp_dir: Path):
    f = tmp_dir / "new.env"
    results = patch_envs([f], {"X": "10"})
    assert f.exists()
    assert results[0].changed is True


# ---------------------------------------------------------------------------
# format_patch_report
# ---------------------------------------------------------------------------

def test_format_patch_report_shows_applied(tmp_dir: Path):
    f = tmp_dir / ".env"
    _write(f, "")
    results = patch_envs([f], {"KEY": "val"})
    report = format_patch_report(results)
    assert "+ KEY" in report
    assert "changed" in report


def test_format_patch_report_shows_skipped(tmp_dir: Path):
    f = tmp_dir / ".env"
    _write(f, "KEY=existing\n")
    results = patch_envs([f], {"KEY": "new"}, overwrite=False)
    report = format_patch_report(results)
    assert "~ KEY (skipped)" in report
