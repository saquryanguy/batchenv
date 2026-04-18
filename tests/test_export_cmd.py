"""Tests for batchenv.commands.export_cmd."""
from __future__ import annotations

import pytest
from pathlib import Path

from batchenv.commands.export_cmd import run


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def test_export_to_file(tmp_dir):
    a = _write(tmp_dir / ".env.a", "KEY1=hello\nKEY2=world\n")
    out = tmp_dir / ".env.out"
    code = run([str(a)], output=str(out))
    assert code == 0
    text = out.read_text()
    assert "KEY1=hello" in text
    assert "KEY2=world" in text


def test_export_to_stdout(tmp_dir, capsys):
    a = _write(tmp_dir / ".env", "FOO=bar\n")
    code = run([str(a)])
    assert code == 0
    captured = capsys.readouterr()
    assert "FOO=bar" in captured.out


def test_export_merge_two_files(tmp_dir):
    a = _write(tmp_dir / ".env.a", "A=1\n")
    b = _write(tmp_dir / ".env.b", "B=2\n")
    out = tmp_dir / ".env.merged"
    code = run([str(a), str(b)], output=str(out))
    assert code == 0
    text = out.read_text()
    assert "A=1" in text
    assert "B=2" in text


def test_export_strategy_first_wins(tmp_dir):
    a = _write(tmp_dir / ".env.a", "KEY=first\n")
    b = _write(tmp_dir / ".env.b", "KEY=second\n")
    out = tmp_dir / ".env.out"
    code = run([str(a), str(b)], output=str(out), strategy="first")
    assert code == 0
    assert "KEY=first" in out.read_text()


def test_export_invalid_strategy(tmp_dir):
    a = _write(tmp_dir / ".env", "X=1\n")
    code = run([str(a)], strategy="unknown")
    assert code == 1


def test_export_missing_source(tmp_dir):
    code = run([str(tmp_dir / "nonexistent.env")])
    assert code == 1


def test_export_no_sources():
    code = run([])
    assert code == 1


def test_export_with_prefix(tmp_dir, capsys):
    a = _write(tmp_dir / ".env", "BAR=baz\n")
    code = run([str(a)], export_prefix=True)
    assert code == 0
    captured = capsys.readouterr()
    assert "export BAR=baz" in captured.out
