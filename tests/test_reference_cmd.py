"""Tests for batchenv.commands.reference_cmd."""
import argparse
from pathlib import Path

import pytest

from batchenv.commands.reference_cmd import run


@pytest.fixture()
def tmp_dir(tmp_path):
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content)
    return p


def _args(files, strict=False):
    ns = argparse.Namespace()
    ns.files = [str(f) for f in files]
    ns.strict = strict
    return ns


def test_reference_cmd_no_refs(tmp_dir, capsys):
    f = _write(tmp_dir / ".env", "A=1\nB=2\n")
    rc = run(_args([f]))
    assert rc == 0
    out = capsys.readouterr().out
    assert "no variable references found" in out


def test_reference_cmd_resolved_refs(tmp_dir, capsys):
    f = _write(tmp_dir / ".env", "HOST=localhost\nPORT=5432\nURL=${HOST}:${PORT}\n")
    rc = run(_args([f]))
    assert rc == 0
    out = capsys.readouterr().out
    assert "URL" in out
    assert "HOST" in out


def test_reference_cmd_missing_ref_non_strict(tmp_dir, capsys):
    f = _write(tmp_dir / ".env", "URL=${HOST}\n")
    rc = run(_args([f], strict=False))
    # non-strict: still exits 0 even with missing refs
    assert rc == 0
    out = capsys.readouterr().out
    assert "MISSING" in out


def test_reference_cmd_missing_ref_strict(tmp_dir):
    f = _write(tmp_dir / ".env", "URL=${HOST}\n")
    rc = run(_args([f], strict=True))
    assert rc == 1


def test_reference_cmd_missing_file(tmp_dir, capsys):
    rc = run(_args([tmp_dir / "ghost.env"]))
    assert rc == 1
    err = capsys.readouterr().err
    assert "not found" in err


def test_reference_cmd_multiple_files(tmp_dir, capsys):
    f1 = _write(tmp_dir / "a.env", "X=1\n")
    f2 = _write(tmp_dir / "b.env", "Y=${X}\n")
    rc = run(_args([f1, f2], strict=True))
    # f2 references X which is not in f2 itself -> strict should fail
    assert rc == 1
