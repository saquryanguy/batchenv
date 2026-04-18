import pytest
from pathlib import Path
from batchenv.commands.placeholder_cmd import run
import argparse


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def _write(p: Path, content: str):
    p.write_text(content)


def _args(**kwargs):
    defaults = {"files": [], "set": None, "overwrite": False, "dry_run": False}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_fills_placeholder(tmp_dir):
    f = tmp_dir / ".env"
    _write(f, "KEY=PLACEHOLDER\n")
    code = run(_args(files=[str(f)], set=["KEY=real"]))
    assert code == 0
    assert "real" in f.read_text()


def test_dry_run_does_not_modify(tmp_dir):
    f = tmp_dir / ".env"
    _write(f, "KEY=\n")
    code = run(_args(files=[str(f)], set=["KEY=val"], dry_run=True))
    assert code == 0
    assert f.read_text() == "KEY=\n"


def test_no_values_returns_error(tmp_dir):
    f = tmp_dir / ".env"
    _write(f, "KEY=\n")
    code = run(_args(files=[str(f)], set=None))
    assert code == 1


def test_missing_file_returns_error(tmp_dir):
    code = run(_args(files=["/nonexistent/.env"], set=["K=v"]))
    assert code == 1


def test_invalid_pair_returns_error(tmp_dir):
    f = tmp_dir / ".env"
    _write(f, "KEY=\n")
    code = run(_args(files=[str(f)], set=["INVALID"]))
    assert code == 1


def test_overwrite_existing(tmp_dir):
    f = tmp_dir / ".env"
    _write(f, "KEY=existing\n")
    code = run(_args(files=[str(f)], set=["KEY=new"], overwrite=True))
    assert code == 0
    assert "new" in f.read_text()
