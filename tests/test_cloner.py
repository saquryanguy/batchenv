"""Tests for batchenv.cloner."""
from pathlib import Path

import pytest

from batchenv.cloner import clone_env, format_clone_report


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_clone_basic(tmp_dir: Path) -> None:
    src = _write(tmp_dir / "src" / ".env", "KEY=value\nFOO=bar\n")
    dest = tmp_dir / "dest" / ".env"
    result = clone_env(src, [dest])
    assert dest.exists()
    assert "KEY=value" in dest.read_text()
    assert result.changed is True
    assert dest in result.destinations
    assert result.skipped == []


def test_clone_dry_run_does_not_write(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "KEY=value\n")
    dest = tmp_dir / "copy" / ".env"
    result = clone_env(src, [dest], dry_run=True)
    assert not dest.exists()
    assert result.changed is True
    assert dest in result.destinations


def test_clone_skips_existing_without_overwrite(tmp_dir: Path) -> None:
    src = _write(tmp_dir / "src.env", "KEY=value\n")
    dest = _write(tmp_dir / "dest.env", "KEY=old\n")
    result = clone_env(src, [dest], overwrite=False)
    assert dest.read_text() == "KEY=old\n"
    assert result.changed is False
    assert dest in result.skipped


def test_clone_overwrites_when_flag_set(tmp_dir: Path) -> None:
    src = _write(tmp_dir / "src.env", "KEY=new\n")
    dest = _write(tmp_dir / "dest.env", "KEY=old\n")
    result = clone_env(src, [dest], overwrite=True)
    assert "KEY=new" in dest.read_text()
    assert result.changed is True
    assert dest in result.destinations


def test_clone_multiple_destinations(tmp_dir: Path) -> None:
    src = _write(tmp_dir / "src.env", "A=1\nB=2\n")
    dests = [tmp_dir / f"copy{i}.env" for i in range(3)]
    result = clone_env(src, dests)
    assert all(d.exists() for d in dests)
    assert len(result.destinations) == 3
    assert result.skipped == []


def test_clone_mixed_existing_and_new(tmp_dir: Path) -> None:
    src = _write(tmp_dir / "src.env", "X=1\n")
    existing = _write(tmp_dir / "existing.env", "X=old\n")
    new_dest = tmp_dir / "new.env"
    result = clone_env(src, [existing, new_dest], overwrite=False)
    assert existing.read_text() == "X=old\n"
    assert new_dest.exists()
    assert existing in result.skipped
    assert new_dest in result.destinations


def test_format_clone_report_lists_cloned(tmp_dir: Path) -> None:
    src = _write(tmp_dir / "src.env", "K=v\n")
    dest = tmp_dir / "out.env"
    result = clone_env(src, [dest])
    report = format_clone_report(result)
    assert "cloned to" in report
    assert str(dest) in report


def test_format_clone_report_lists_skipped(tmp_dir: Path) -> None:
    src = _write(tmp_dir / "src.env", "K=v\n")
    dest = _write(tmp_dir / "dest.env", "K=old\n")
    result = clone_env(src, [dest], overwrite=False)
    report = format_clone_report(result)
    assert "skipped" in report
    assert str(dest) in report
