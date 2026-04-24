"""Tests for the `profile` CLI command."""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from batchenv.profiler_cmd import run


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(directory: Path, name: str, content: str) -> Path:
    p = directory / name
    p.write_text(content)
    return p


def _args(files: list[Path]) -> argparse.Namespace:
    return argparse.Namespace(files=[str(f) for f in files])


def test_profile_single_file(tmp_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    f = _write(tmp_dir, ".env", "KEY=value\nDB_HOST=localhost\n# comment\n")
    rc = run(_args([f]))
    assert rc == 0
    out = capsys.readouterr().out
    assert ".env" in out
    assert "keys" in out.lower() or "key" in out.lower()


def test_profile_multiple_files(tmp_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    f1 = _write(tmp_dir, ".env.dev", "A=1\nB=2\n")
    f2 = _write(tmp_dir, ".env.prod", "A=prod\nB=prod\nC=extra\n")
    rc = run(_args([f1, f2]))
    assert rc == 0
    out = capsys.readouterr().out
    assert ".env.dev" in out
    assert ".env.prod" in out


def test_profile_missing_file_returns_error(
    tmp_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_dir / "nonexistent.env"
    rc = run(_args([missing]))
    assert rc == 1
    out = capsys.readouterr().out
    assert "error" in out.lower()


def test_profile_empty_file(tmp_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    f = _write(tmp_dir, ".env", "")
    rc = run(_args([f]))
    assert rc == 0
    out = capsys.readouterr().out
    assert ".env" in out


def test_profile_blank_and_comment_ratios(
    tmp_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    content = "# header\n\nKEY=val\n\n# another\nSECRET=abc\n"
    f = _write(tmp_dir, ".env", content)
    rc = run(_args([f]))
    assert rc == 0
    out = capsys.readouterr().out
    # Report should mention blank or comment ratio metrics
    assert any(word in out.lower() for word in ("blank", "comment", "ratio"))
