"""Tests for batchenv.commands.tag_cmd."""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from batchenv.commands.tag_cmd import run


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content)
    return p


def _args(**kwargs) -> argparse.Namespace:
    defaults = {
        "files": [],
        "tag": None,
        "overwrite": False,
        "dry_run": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_tag_cmd_basic(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "DB_HOST=localhost\nAPP=web\n")
    rc = run(_args(files=[str(f)], tag=["DB_HOST=database host"]))
    assert rc == 0
    content = f.read_text()
    assert "# database host" in content
    assert "APP=web" in content


def test_tag_cmd_dry_run_does_not_modify(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "KEY=value\n")
    original = f.read_text()
    rc = run(_args(files=[str(f)], tag=["KEY=my tag"], dry_run=True))
    assert rc == 0
    assert f.read_text() == original


def test_tag_cmd_no_tags_returns_error(tmp_dir: Path, capsys):
    f = _write(tmp_dir / ".env", "KEY=value\n")
    rc = run(_args(files=[str(f)], tag=None))
    assert rc == 1
    captured = capsys.readouterr()
    assert "required" in captured.err


def test_tag_cmd_missing_file_returns_error(tmp_dir: Path, capsys):
    rc = run(_args(files=["/nonexistent/.env"], tag=["KEY=tag"]))
    assert rc == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_tag_cmd_overwrite_replaces_comment(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "HOST=localhost  # old\n")
    rc = run(_args(files=[str(f)], tag=["HOST=new comment"], overwrite=True))
    assert rc == 0
    content = f.read_text()
    assert "# new comment" in content
    assert "# old" not in content


def test_tag_cmd_skip_existing_without_overwrite(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "HOST=localhost  # existing\n")
    rc = run(_args(files=[str(f)], tag=["HOST=new comment"], overwrite=False))
    assert rc == 0
    content = f.read_text()
    assert "# existing" in content
    assert "# new comment" not in content
