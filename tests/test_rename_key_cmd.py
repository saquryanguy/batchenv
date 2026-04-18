"""Tests for the rename-key command."""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from batchenv.commands.rename_key_cmd import run


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> None:
    path.write_text(content)


def _args(**kwargs) -> argparse.Namespace:
    defaults = {"old_key": "OLD", "new_key": "NEW", "files": [], "force": False, "dry_run": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_rename_key_basic(tmp_dir: Path) -> None:
    f = tmp_dir / ".env"
    _write(f, "OLD=hello\nOTHER=world\n")
    args = _args(old_key="OLD", new_key="NEW", files=[str(f)])
    rc = run(args)
    assert rc == 0
    content = f.read_text()
    assert "NEW=hello" in content
    assert "OLD" not in content


def test_rename_key_dry_run_does_not_modify(tmp_dir: Path) -> None:
    f = tmp_dir / ".env"
    _write(f, "OLD=hello\n")
    args = _args(old_key="OLD", new_key="NEW", files=[str(f)], dry_run=True)
    rc = run(args)
    assert rc == 0
    assert "OLD=hello" in f.read_text()


def test_rename_key_missing_file(tmp_dir: Path) -> None:
    f = tmp_dir / "ghost.env"
    args = _args(old_key="OLD", new_key="NEW", files=[str(f)])
    rc = run(args)
    assert rc == 1


def test_rename_key_skips_when_key_absent(tmp_dir: Path) -> None:
    f = tmp_dir / ".env"
    _write(f, "KEEP=value\n")
    original = f.read_text()
    args = _args(old_key="MISSING", new_key="NEW", files=[str(f)])
    rc = run(args)
    assert rc == 0
    assert f.read_text() == original


def test_rename_key_no_overwrite_by_default(tmp_dir: Path) -> None:
    f = tmp_dir / ".env"
    _write(f, "OLD=1\nNEW=2\n")
    args = _args(old_key="OLD", new_key="NEW", files=[str(f)])
    rc = run(args)
    assert rc == 0
    content = f.read_text()
    # NEW should not be overwritten; OLD remains unchanged
    assert "OLD=1" in content


def test_rename_key_force_overwrites(tmp_dir: Path) -> None:
    f = tmp_dir / ".env"
    _write(f, "OLD=1\nNEW=2\n")
    args = _args(old_key="OLD", new_key="NEW", files=[str(f)], force=True)
    rc = run(args)
    assert rc == 0
    content = f.read_text()
    assert "OLD" not in content
    assert "NEW=1" in content
