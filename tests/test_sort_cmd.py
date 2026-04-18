import pytest
from pathlib import Path
from batchenv.commands.sort_cmd import run
from batchenv.parser import parse_env_file


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def _write(p: Path, content: str):
    p.write_text(content)


def test_sort_writes_sorted_file(tmp_dir):
    f = tmp_dir / ".env"
    _write(f, "ZEBRA=1\nAPPLE=2\n")
    result = run([str(f)])
    assert result == 0
    env = parse_env_file(f)
    assert list(env.keys()) == ["APPLE", "ZEBRA"]


def test_sort_dry_run_does_not_modify(tmp_dir):
    f = tmp_dir / ".env"
    _write(f, "ZEBRA=1\nAPPLE=2\n")
    run(["--dry-run", str(f)])
    env = parse_env_file(f)
    assert list(env.keys()) == ["ZEBRA", "APPLE"]


def test_sort_reverse(tmp_dir):
    f = tmp_dir / ".env"
    _write(f, "APPLE=1\nZEBRA=2\nMANGO=3\n")
    run(["--reverse", str(f)])
    env = parse_env_file(f)
    assert list(env.keys()) == ["ZEBRA", "MANGO", "APPLE"]


def test_sort_missing_file(tmp_dir):
    result = run([str(tmp_dir / "missing.env")])
    assert result == 1


def test_sort_already_sorted_unchanged(tmp_dir):
    f = tmp_dir / ".env"
    original = "ALPHA=1\nBETA=2\n"
    _write(f, original)
    run([str(f)])
    assert f.read_text() == original
