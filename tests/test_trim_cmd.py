import pytest
from pathlib import Path
from types import SimpleNamespace
from batchenv.commands.trim_cmd import run


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def _write(path, content):
    path.write_text(content)


def test_trim_removes_extra_keys(tmp_dir):
    ref = tmp_dir / ".env.ref"
    target = tmp_dir / ".env"
    _write(ref, "A=1\nB=2\n")
    _write(target, "A=1\nB=2\nC=3\n")
    args = SimpleNamespace(reference=str(ref), files=[str(target)], dry_run=False, verbose=False)
    run(args)
    result = target.read_text()
    assert "C" not in result
    assert "A=1" in result


def test_trim_dry_run_does_not_modify(tmp_dir):
    ref = tmp_dir / ".env.ref"
    target = tmp_dir / ".env"
    _write(ref, "A=1\n")
    _write(target, "A=1\nB=2\n")
    original = target.read_text()
    args = SimpleNamespace(reference=str(ref), files=[str(target)], dry_run=True, verbose=False)
    run(args)
    assert target.read_text() == original


def test_trim_no_change_when_keys_match(tmp_dir):
    ref = tmp_dir / ".env.ref"
    target = tmp_dir / ".env"
    _write(ref, "A=1\nB=2\n")
    _write(target, "A=1\nB=2\n")
    args = SimpleNamespace(reference=str(ref), files=[str(target)], dry_run=False, verbose=False)
    run(args)
    assert "A=1" in target.read_text()
    assert "B=2" in target.read_text()


def test_trim_missing_file_returns_error(tmp_dir):
    ref = tmp_dir / ".env.ref"
    _write(ref, "A=1\n")
    args = SimpleNamespace(reference=str(ref), files=[str(tmp_dir / "missing.env")], dry_run=False, verbose=False)
    result = run(args)
    assert result == 1


def test_trim_missing_reference_returns_error(tmp_dir):
    target = tmp_dir / ".env"
    _write(target, "A=1\n")
    args = SimpleNamespace(reference=str(tmp_dir / "missing.ref"), files=[str(target)], dry_run=False, verbose=False)
    result = run(args)
    assert result == 1


def test_trim_verbose_output(tmp_dir, capsys):
    ref = tmp_dir / ".env.ref"
    target = tmp_dir / ".env"
    _write(ref, "A=1\n")
    _write(target, "A=1\nEXTRA=99\n")
    args = SimpleNamespace(reference=str(ref), files=[str(target)], dry_run=False, verbose=True)
    run(args)
    captured = capsys.readouterr()
    assert "updated" in captured.out
