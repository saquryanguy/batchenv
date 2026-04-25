"""Tests for batchenv.pinner."""
from pathlib import Path

import pytest

from batchenv.pinner import PinResult, pin_env, pin_envs, format_pin_report


# ---------------------------------------------------------------------------
# Unit tests for pin_env
# ---------------------------------------------------------------------------

def test_pin_env_adds_new_key():
    env = {"A": "1"}
    new_env, pinned, skipped = pin_env(env, {"B": "2"})
    assert new_env["B"] == "2"
    assert "B" in pinned
    assert skipped == []


def test_pin_env_overwrites_existing_by_default():
    env = {"A": "old"}
    new_env, pinned, skipped = pin_env(env, {"A": "new"})
    assert new_env["A"] == "new"
    assert "A" in pinned
    assert skipped == []


def test_pin_env_skips_existing_when_no_overwrite():
    env = {"A": "old"}
    new_env, pinned, skipped = pin_env(env, {"A": "new"}, overwrite=False)
    assert new_env["A"] == "old"
    assert "A" in skipped
    assert pinned == []


def test_pin_env_does_not_mutate_original():
    env = {"A": "1"}
    pin_env(env, {"A": "99"})
    assert env["A"] == "1"


def test_pin_env_multiple_pins():
    env = {"A": "1", "B": "2"}
    new_env, pinned, skipped = pin_env(env, {"A": "10", "C": "30"})
    assert new_env["A"] == "10"
    assert new_env["C"] == "30"
    assert set(pinned) == {"A", "C"}


# ---------------------------------------------------------------------------
# Integration tests for pin_envs
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> None:
    path.write_text(content)


def test_pin_envs_writes_file(tmp_dir: Path):
    f = tmp_dir / ".env"
    _write(f, "HOST=localhost\nPORT=8080\n")
    results = pin_envs([f], {"HOST": "prod.example.com"})
    assert results[0].changed
    assert "HOST=prod.example.com" in f.read_text()


def test_pin_envs_dry_run_does_not_modify(tmp_dir: Path):
    f = tmp_dir / ".env"
    original = "HOST=localhost\n"
    _write(f, original)
    pin_envs([f], {"HOST": "prod.example.com"}, dry_run=True)
    assert f.read_text() == original


def test_pin_envs_no_overwrite_skips(tmp_dir: Path):
    f = tmp_dir / ".env"
    _write(f, "HOST=localhost\n")
    results = pin_envs([f], {"HOST": "prod.example.com"}, overwrite=False)
    assert not results[0].changed
    assert "HOST" in results[0].skipped


def test_pin_envs_multiple_files(tmp_dir: Path):
    f1 = tmp_dir / ".env.staging"
    f2 = tmp_dir / ".env.prod"
    _write(f1, "DB=old\n")
    _write(f2, "DB=old\n")
    results = pin_envs([f1, f2], {"DB": "new"})
    assert all(r.changed for r in results)
    assert "DB=new" in f1.read_text()
    assert "DB=new" in f2.read_text()


# ---------------------------------------------------------------------------
# format_pin_report
# ---------------------------------------------------------------------------

def test_format_pin_report_shows_status():
    r = PinResult(path=Path(".env"), pinned=["A"], skipped=["B"], changed=True)
    report = format_pin_report([r])
    assert ".env" in report
    assert "pinned" in report
    assert "skipped" in report
    assert "changed" in report


def test_format_pin_report_unchanged():
    r = PinResult(path=Path(".env"), pinned=[], skipped=[], changed=False)
    report = format_pin_report([r])
    assert "unchanged" in report
