"""Tests for batchenv.commands.pin_cmd."""
from pathlib import Path
from types import SimpleNamespace

import pytest

from batchenv.commands.pin_cmd import run


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> None:
    path.write_text(content)


def _args(**kwargs):
    defaults = dict(files=[], pin=[], no_overwrite=False, dry_run=False)
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_pin_cmd_basic(tmp_dir: Path):
    f = tmp_dir / ".env"
    _write(f, "HOST=localhost\nPORT=8080\n")
    rc = run(_args(files=[str(f)], pin=["HOST=prod.example.com"]))
    assert rc == 0
    assert "HOST=prod.example.com" in f.read_text()


def test_pin_cmd_dry_run_does_not_modify(tmp_dir: Path):
    f = tmp_dir / ".env"
    original = "HOST=localhost\n"
    _write(f, original)
    rc = run(_args(files=[str(f)], pin=["HOST=prod.example.com"], dry_run=True))
    assert rc == 0
    assert f.read_text() == original


def test_pin_cmd_no_overwrite_skips_existing(tmp_dir: Path):
    f = tmp_dir / ".env"
    _write(f, "HOST=localhost\n")
    rc = run(_args(files=[str(f)], pin=["HOST=prod.example.com"], no_overwrite=True))
    assert rc == 0
    assert "HOST=localhost" in f.read_text()


def test_pin_cmd_missing_file_returns_error(tmp_dir: Path):
    f = tmp_dir / "nonexistent.env"
    rc = run(_args(files=[str(f)], pin=["A=1"]))
    assert rc == 1


def test_pin_cmd_no_pins_returns_error(tmp_dir: Path):
    f = tmp_dir / ".env"
    _write(f, "A=1\n")
    rc = run(_args(files=[str(f)], pin=[]))
    assert rc == 1


def test_pin_cmd_invalid_pin_format_exits(tmp_dir: Path):
    f = tmp_dir / ".env"
    _write(f, "A=1\n")
    with pytest.raises(SystemExit):
        run(_args(files=[str(f)], pin=["BADFORMAT"]))


def test_pin_cmd_multiple_files(tmp_dir: Path):
    f1 = tmp_dir / ".env.staging"
    f2 = tmp_dir / ".env.prod"
    _write(f1, "DB=old\n")
    _write(f2, "DB=old\n")
    rc = run(_args(files=[str(f1), str(f2)], pin=["DB=new"]))
    assert rc == 0
    assert "DB=new" in f1.read_text()
    assert "DB=new" in f2.read_text()
