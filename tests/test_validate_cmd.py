"""Tests for batchenv.commands.validate_cmd."""
from pathlib import Path

import pytest

from batchenv.commands.validate_cmd import run


@pytest.fixture()
def tmp_dir(tmp_path: Path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def test_validate_all_valid(tmp_dir):
    ref = _write(tmp_dir / ".env.ref", "HOST=localhost\nPORT=5432\n")
    t1 = _write(tmp_dir / ".env", "HOST=prod\nPORT=5433\n")
    assert run(str(ref), [str(t1)]) == 0


def test_validate_missing_key(tmp_dir):
    ref = _write(tmp_dir / ".env.ref", "HOST=localhost\nPORT=5432\n")
    t1 = _write(tmp_dir / ".env", "HOST=prod\n")
    assert run(str(ref), [str(t1)]) == 1


def test_validate_extra_key_not_strict(tmp_dir):
    ref = _write(tmp_dir / ".env.ref", "HOST=localhost\n")
    t1 = _write(tmp_dir / ".env", "HOST=prod\nEXTRA=yes\n")
    assert run(str(ref), [str(t1)]) == 0


def test_validate_extra_key_strict(tmp_dir):
    ref = _write(tmp_dir / ".env.ref", "HOST=localhost\n")
    t1 = _write(tmp_dir / ".env", "HOST=prod\nEXTRA=yes\n")
    assert run(str(ref), [str(t1)], strict=True) == 1


def test_validate_missing_reference(tmp_dir):
    assert run(str(tmp_dir / "ghost.env"), []) == 2


def test_validate_no_valid_targets(tmp_dir):
    ref = _write(tmp_dir / ".env.ref", "HOST=localhost\n")
    assert run(str(ref), [str(tmp_dir / "missing.env")]) == 2


def test_validate_quiet_suppresses_output(tmp_dir, capsys):
    ref = _write(tmp_dir / ".env.ref", "HOST=localhost\n")
    t1 = _write(tmp_dir / ".env", "HOST=prod\n")
    run(str(ref), [str(t1)], quiet=True)
    captured = capsys.readouterr()
    assert captured.out == ""
