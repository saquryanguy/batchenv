"""Tests for batchenv.commands.stripcomments_cmd."""
import pytest
from pathlib import Path

from batchenv.commands.stripcomments_cmd import run


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def test_strips_comments_from_file(tmp_dir):
    p = _write(tmp_dir / ".env", "# comment\nKEY=val\n")
    code = run([str(p)])
    assert code == 0
    assert "# comment" not in p.read_text()
    assert "KEY=val" in p.read_text()


def test_dry_run_does_not_modify(tmp_dir):
    content = "# comment\nKEY=val\n"
    p = _write(tmp_dir / ".env", content)
    code = run([str(p)], dry_run=True)
    assert code == 0
    assert p.read_text() == content


def test_missing_file_returns_error(tmp_dir):
    code = run([str(tmp_dir / "nonexistent.env")])
    assert code == 1


def test_no_comments_unchanged(tmp_dir):
    content = "A=1\nB=2\n"
    p = _write(tmp_dir / ".env", content)
    run([str(p)])
    assert p.read_text() == content


def test_quiet_suppresses_output(tmp_dir, capsys):
    p = _write(tmp_dir / ".env", "# x\nKEY=1\n")
    run([str(p)], quiet=True)
    captured = capsys.readouterr()
    assert captured.out == ""
