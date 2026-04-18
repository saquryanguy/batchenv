"""Tests for batchenv.commands.list_cmd."""
from __future__ import annotations

import io
from pathlib import Path

import pytest

from batchenv.commands.list_cmd import find_env_files, run


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


# ---------------------------------------------------------------------------
# find_env_files
# ---------------------------------------------------------------------------

def test_find_env_files_single(tmp_dir: Path) -> None:
    _write(tmp_dir / ".env", "A=1\n")
    result = find_env_files(str(tmp_dir))
    assert len(result) == 1
    assert result[0].name == ".env"


def test_find_env_files_multiple_variants(tmp_dir: Path) -> None:
    _write(tmp_dir / ".env", "A=1\n")
    _write(tmp_dir / ".env.local", "B=2\n")
    _write(tmp_dir / ".env.production", "C=3\n")
    result = find_env_files(str(tmp_dir))
    assert len(result) == 3


def test_find_env_files_nested(tmp_dir: Path) -> None:
    _write(tmp_dir / "sub" / ".env", "X=1\n")
    _write(tmp_dir / "other" / "deep" / ".env", "Y=2\n")
    result = find_env_files(str(tmp_dir))
    assert len(result) == 2


def test_find_env_files_no_match(tmp_dir: Path) -> None:
    _write(tmp_dir / "config.yaml", "key: val\n")
    result = find_env_files(str(tmp_dir))
    assert result == []


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------

def test_run_lists_files(tmp_dir: Path) -> None:
    _write(tmp_dir / ".env", "A=1\n")
    out = io.StringIO()
    run([str(tmp_dir)], output=out)
    assert ".env" in out.getvalue()


def test_run_no_files_message(tmp_dir: Path) -> None:
    out = io.StringIO()
    run([str(tmp_dir)], output=out)
    assert "no env files found" in out.getvalue()


def test_run_show_keys(tmp_dir: Path) -> None:
    _write(tmp_dir / ".env", "FOO=bar\nBAZ=qux\n")
    out = io.StringIO()
    run([str(tmp_dir)], show_keys=True, output=out)
    text = out.getvalue()
    assert "FOO" in text
    assert "BAZ" in text


def test_run_multiple_directories(tmp_dir: Path) -> None:
    dir_a = tmp_dir / "a"
    dir_b = tmp_dir / "b"
    _write(dir_a / ".env", "A=1\n")
    _write(dir_b / ".env", "B=2\n")
    out = io.StringIO()
    run([str(dir_a), str(dir_b)], output=out)
    text = out.getvalue()
    assert str(dir_a / ".env") in text
    assert str(dir_b / ".env") in text
