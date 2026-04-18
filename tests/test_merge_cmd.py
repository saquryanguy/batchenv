import pytest
from pathlib import Path
from batchenv.commands.merge_cmd import run


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def _write(directory: Path, name: str, content: str) -> str:
    p = directory / name
    p.write_text(content)
    return str(p)


def test_merge_no_conflict(tmp_dir, capsys):
    a = _write(tmp_dir, "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp_dir, "b.env", "BAZ=3\n")
    code = run([a, b], quiet=True, dry_run=True)
    assert code == 0


def test_merge_writes_output(tmp_dir):
    a = _write(tmp_dir, "a.env", "FOO=hello\n")
    b = _write(tmp_dir, "b.env", "BAR=world\n")
    out = str(tmp_dir / "merged.env")
    code = run([a, b], output=out, quiet=True)
    assert code == 0
    content = Path(out).read_text()
    assert "FOO=hello" in content
    assert "BAR=world" in content


def test_merge_conflict_first(tmp_dir, capsys):
    a = _write(tmp_dir, "a.env", "KEY=alpha\n")
    b = _write(tmp_dir, "b.env", "KEY=beta\n")
    out = str(tmp_dir / "out.env")
    code = run([a, b], output=out, strategy="first", quiet=True)
    assert code == 0
    assert "KEY=alpha" in Path(out).read_text()


def test_merge_conflict_last(tmp_dir):
    a = _write(tmp_dir, "a.env", "KEY=alpha\n")
    b = _write(tmp_dir, "b.env", "KEY=beta\n")
    out = str(tmp_dir / "out.env")
    run([a, b], output=out, strategy="last", quiet=True)
    assert "KEY=beta" in Path(out).read_text()


def test_merge_conflict_error_strategy(tmp_dir):
    a = _write(tmp_dir, "a.env", "KEY=x\n")
    b = _write(tmp_dir, "b.env", "KEY=y\n")
    code = run([a, b], strategy="error", quiet=True)
    assert code == 1


def test_merge_missing_file(tmp_dir):
    code = run([str(tmp_dir / "ghost.env")], quiet=True)
    assert code == 2


def test_merge_invalid_strategy(tmp_dir):
    a = _write(tmp_dir, "a.env", "X=1\n")
    code = run([a], strategy="unknown")
    assert code == 2


def test_dry_run_does_not_write(tmp_dir):
    a = _write(tmp_dir, "a.env", "FOO=1\n")
    out = str(tmp_dir / "out.env")
    run([a], output=out, dry_run=True, quiet=True)
    assert not Path(out).exists()
