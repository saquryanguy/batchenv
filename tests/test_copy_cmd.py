"""Tests for batchenv.commands.copy_cmd."""
from __future__ import annotations

from pathlib import Path

import pytest

from batchenv.commands.copy_cmd import run
from batchenv.parser import parse_env_file


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def test_copy_basic_key(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env.src", "FOO=bar\nBAZ=qux\n")
    tgt = _write(tmp_dir / ".env.tgt", "EXISTING=yes\n")
    result = run(str(src), str(tgt), ["FOO"])
    assert result == 0
    env = parse_env_file(tgt)
    assert env["FOO"] == "bar"
    assert env["EXISTING"] == "yes"


def test_copy_does_not_overwrite_by_default(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env.src", "FOO=new\n")
    tgt = _write(tmp_dir / ".env.tgt", "FOO=old\n")
    run(str(src), str(tgt), ["FOO"])
    env = parse_env_file(tgt)
    assert env["FOO"] == "old"


def test_copy_overwrite_flag(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env.src", "FOO=new\n")
    tgt = _write(tmp_dir / ".env.tgt", "FOO=old\n")
    run(str(src), str(tgt), ["FOO"], overwrite=True)
    env = parse_env_file(tgt)
    assert env["FOO"] == "new"


def test_copy_dry_run_does_not_write(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env.src", "FOO=bar\n")
    tgt = _write(tmp_dir / ".env.tgt", "EXISTING=yes\n")
    run(str(src), str(tgt), ["FOO"], dry_run=True)
    env = parse_env_file(tgt)
    assert "FOO" not in env


def test_copy_fill_value_for_missing_key(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env.src", "FOO=bar\n")
    tgt = _write(tmp_dir / ".env.tgt", "")
    run(str(src), str(tgt), ["FOO", "MISSING"], fill_value="CHANGEME")
    env = parse_env_file(tgt)
    assert env["FOO"] == "bar"
    assert env["MISSING"] == "CHANGEME"


def test_copy_missing_source_returns_error(tmp_dir: Path) -> None:
    tgt = _write(tmp_dir / ".env.tgt", "")
    result = run(str(tmp_dir / "nonexistent"), str(tgt), ["FOO"])
    assert result == 1


def test_copy_creates_target_if_missing(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env.src", "KEY=value\n")
    tgt = tmp_dir / ".env.new"
    assert not tgt.exists()
    run(str(src), str(tgt), ["KEY"])
    assert tgt.exists()
    env = parse_env_file(tgt)
    assert env["KEY"] == "value"
