"""Tests for batchenv.commands.flatten_cmd."""
from argparse import Namespace
from pathlib import Path

import pytest

from batchenv.commands.flatten_cmd import run


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def _args(**kwargs) -> Namespace:
    defaults = dict(
        files=[],
        prefix="",
        separator="__",
        overwrite=False,
        output="",
        dry_run=False,
    )
    defaults.update(kwargs)
    return Namespace(**defaults)


def test_flatten_writes_output_file(tmp_dir):
    a = _write(tmp_dir / "svc.env", "HOST=localhost\n")
    out = tmp_dir / "flat.env"
    args = _args(files=[str(a)], output=str(out))
    rc = run(args)
    assert rc == 0
    assert out.exists()
    content = out.read_text()
    assert "SVC__HOST" in content


def test_flatten_dry_run_does_not_write(tmp_dir):
    a = _write(tmp_dir / "app.env", "KEY=val\n")
    out = tmp_dir / "flat.env"
    args = _args(files=[str(a)], output=str(out), dry_run=True)
    rc = run(args)
    assert rc == 0
    assert not out.exists()


def test_flatten_missing_file_returns_error(tmp_dir):
    args = _args(files=[str(tmp_dir / "missing.env")])
    rc = run(args)
    assert rc == 1


def test_flatten_stdout_when_no_output(tmp_dir, capsys):
    a = _write(tmp_dir / "db.env", "NAME=mydb\n")
    args = _args(files=[str(a)])
    rc = run(args)
    assert rc == 0
    captured = capsys.readouterr()
    assert "DB__NAME" in captured.out


def test_flatten_static_prefix(tmp_dir):
    a = _write(tmp_dir / "svc.env", "PORT=9000\n")
    out = tmp_dir / "flat.env"
    args = _args(files=[str(a)], prefix="MYAPP", output=str(out))
    rc = run(args)
    assert rc == 0
    assert "MYAPP__PORT" in out.read_text()


def test_flatten_overwrite_flag(tmp_dir):
    a = _write(tmp_dir / "first.env", "K=one\n")
    b = _write(tmp_dir / "second.env", "K=two\n")
    out = tmp_dir / "flat.env"
    args = _args(files=[str(a), str(b)], prefix="P", overwrite=True, output=str(out))
    rc = run(args)
    assert rc == 0
    assert "P__K=two" in out.read_text()
