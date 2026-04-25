"""Tests for batchenv.commands.diff_matrix_cmd."""
from pathlib import Path

import pytest

from batchenv.commands.diff_matrix_cmd import run


@pytest.fixture()
def tmp_dir(tmp_path: Path):
    return tmp_path


def _write(directory: Path, name: str, content: str) -> Path:
    p = directory / name
    p.write_text(content)
    return p


class _Args:
    def __init__(self, files, fail_on_diff=False):
        self.files = files
        self.fail_on_diff = fail_on_diff


def test_diff_matrix_identical_files_exit_zero(tmp_dir, capsys):
    a = _write(tmp_dir, "a.env", "KEY=value\n")
    b = _write(tmp_dir, "b.env", "KEY=value\n")
    code = run(_Args([str(a), str(b)]))
    assert code == 0
    out = capsys.readouterr().out
    assert "identical" in out


def test_diff_matrix_differences_exit_zero_without_flag(tmp_dir, capsys):
    a = _write(tmp_dir, "a.env", "KEY=old\n")
    b = _write(tmp_dir, "b.env", "KEY=new\n")
    code = run(_Args([str(a), str(b)]))
    assert code == 0


def test_diff_matrix_fail_on_diff_returns_two(tmp_dir):
    a = _write(tmp_dir, "a.env", "KEY=old\n")
    b = _write(tmp_dir, "b.env", "KEY=new\n")
    code = run(_Args([str(a), str(b)], fail_on_diff=True))
    assert code == 2


def test_diff_matrix_no_diff_fail_flag_still_zero(tmp_dir):
    a = _write(tmp_dir, "a.env", "KEY=same\n")
    b = _write(tmp_dir, "b.env", "KEY=same\n")
    code = run(_Args([str(a), str(b)], fail_on_diff=True))
    assert code == 0


def test_diff_matrix_missing_file_returns_one(tmp_dir, capsys):
    a = _write(tmp_dir, "a.env", "KEY=val\n")
    code = run(_Args([str(a), str(tmp_dir / "missing.env")]))
    assert code == 1
    assert "not found" in capsys.readouterr().err


def test_diff_matrix_single_file_returns_one(tmp_dir, capsys):
    a = _write(tmp_dir, "a.env", "KEY=val\n")
    code = run(_Args([str(a)]))
    assert code == 1


def test_diff_matrix_three_files_report(tmp_dir, capsys):
    a = _write(tmp_dir, "a.env", "A=1\n")
    b = _write(tmp_dir, "b.env", "B=2\n")
    c = _write(tmp_dir, "c.env", "C=3\n")
    code = run(_Args([str(a), str(b), str(c)]))
    assert code == 0
    out = capsys.readouterr().out
    # Three pairs should appear
    assert out.count("vs") == 3
