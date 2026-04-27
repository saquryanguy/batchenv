"""Tests for batchenv.commands.filter_cmd."""
from pathlib import Path
from types import SimpleNamespace

import pytest

from batchenv.commands.filter_cmd import run


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def _args(**kwargs):
    defaults = dict(
        files=[],
        key_pattern=None,
        value_pattern=None,
        invert=False,
        dry_run=False,
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_filter_cmd_removes_non_matching_keys(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "DB_HOST=localhost\nDB_PORT=5432\nAPP_NAME=myapp\n")
    args = _args(files=[str(f)], key_pattern=r"^DB_")
    rc = run(args)
    assert rc == 0
    content = f.read_text()
    assert "DB_HOST" in content
    assert "DB_PORT" in content
    assert "APP_NAME" not in content


def test_filter_cmd_dry_run_does_not_modify(tmp_dir: Path):
    original = "DB_HOST=localhost\nAPP_NAME=myapp\n"
    f = _write(tmp_dir / ".env", original)
    args = _args(files=[str(f)], key_pattern=r"^DB_", dry_run=True)
    rc = run(args)
    assert rc == 0
    assert f.read_text() == original


def test_filter_cmd_missing_file_returns_error(tmp_dir: Path):
    args = _args(files=[str(tmp_dir / "nonexistent.env")], key_pattern=r"DB")
    rc = run(args)
    assert rc == 1


def test_filter_cmd_no_patterns_returns_error(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "A=1\n")
    args = _args(files=[str(f)])
    rc = run(args)
    assert rc == 1


def test_filter_cmd_invert_removes_matching(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "SECRET_KEY=abc\nAPP_NAME=myapp\nSECRET_TOKEN=xyz\n")
    args = _args(files=[str(f)], key_pattern=r"^SECRET_", invert=True)
    rc = run(args)
    assert rc == 0
    content = f.read_text()
    assert "APP_NAME" in content
    assert "SECRET_KEY" not in content
    assert "SECRET_TOKEN" not in content


def test_filter_cmd_value_pattern(tmp_dir: Path):
    f = _write(tmp_dir / ".env", "HOST=localhost\nPORT=5432\nDEBUG=true\n")
    args = _args(files=[str(f)], value_pattern=r"^\d+$")
    rc = run(args)
    assert rc == 0
    content = f.read_text()
    assert "PORT" in content
    assert "HOST" not in content
    assert "DEBUG" not in content


def test_filter_cmd_unchanged_file_not_rewritten(tmp_dir: Path):
    original = "DB_HOST=localhost\nDB_PORT=5432\n"
    f = _write(tmp_dir / ".env", original)
    mtime_before = f.stat().st_mtime_ns
    args = _args(files=[str(f)], key_pattern=r"^DB_")
    run(args)
    # File should not have been rewritten since nothing changed
    assert f.stat().st_mtime_ns == mtime_before
