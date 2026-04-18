"""Tests for batchenv.commands.sync_cmd."""
from __future__ import annotations

from pathlib import Path

import pytest

from batchenv.commands.sync_cmd import run
from batchenv.parser import parse_env_file


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def test_sync_adds_missing_keys(tmp_dir: Path) -> None:
    source = _write(tmp_dir / ".env.source", "A=1\nB=2\nC=3\n")
    target = _write(tmp_dir / ".env.target", "A=1\n")

    code = run(str(source), [str(target)])

    assert code == 0
    result = parse_env_file(target)
    assert result["A"] == "1"
    assert result["B"] == "2"
    assert result["C"] == "3"


def test_sync_dry_run_does_not_modify(tmp_dir: Path) -> None:
    source = _write(tmp_dir / ".env.source", "A=1\nB=2\n")
    target = _write(tmp_dir / ".env.target", "A=1\n")
    original = target.read_text()

    code = run(str(source), [str(target)], dry_run=True)

    assert code == 0
    assert target.read_text() == original


def test_sync_fill_value(tmp_dir: Path) -> None:
    source = _write(tmp_dir / ".env.source", "A=secret\nB=other\n")
    target = _write(tmp_dir / ".env.target", "A=secret\n")

    run(str(source), [str(target)], fill_value="")

    result = parse_env_file(target)
    assert result["B"] == ""


def test_sync_overwrite_changed(tmp_dir: Path) -> None:
    source = _write(tmp_dir / ".env.source", "A=new\n")
    target = _write(tmp_dir / ".env.target", "A=old\n")

    run(str(source), [str(target)], overwrite=True)

    result = parse_env_file(target)
    assert result["A"] == "new"


def test_sync_no_overwrite_by_default(tmp_dir: Path) -> None:
    source = _write(tmp_dir / ".env.source", "A=new\n")
    target = _write(tmp_dir / ".env.target", "A=old\n")

    run(str(source), [str(target)])

    result = parse_env_file(target)
    assert result["A"] == "old"


def test_sync_missing_source_returns_error(tmp_dir: Path) -> None:
    target = _write(tmp_dir / ".env.target", "A=1\n")
    code = run(str(tmp_dir / "nonexistent"), [str(target)])
    assert code == 1


def test_sync_missing_target_returns_error(tmp_dir: Path) -> None:
    source = _write(tmp_dir / ".env.source", "A=1\n")
    code = run(str(source), [str(tmp_dir / "nonexistent")])
    assert code == 1
