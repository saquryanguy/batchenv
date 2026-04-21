"""Tests for batchenv.commentstripper."""
import pytest
from pathlib import Path

from batchenv.commentstripper import (
    strip_comments_env,
    strip_comments_envs,
    format_strip_comments_report,
)


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def test_strip_comments_env_removes_comments():
    env = {"#comment": "", "KEY": "value", "# another": ""}
    result = strip_comments_env(env)
    assert result == {"KEY": "value"}


def test_strip_comments_env_no_comments():
    env = {"A": "1", "B": "2"}
    assert strip_comments_env(env) == env


def test_strip_comments_env_empty():
    assert strip_comments_env({}) == {}


def test_strip_comments_envs_changed(tmp_dir):
    p = _write(tmp_dir / ".env", "# comment\nKEY=val\n")
    results = strip_comments_envs([p])
    assert len(results) == 1
    assert results[0].changed is True
    assert results[0].stripped_lines == 1


def test_strip_comments_envs_unchanged(tmp_dir):
    p = _write(tmp_dir / ".env", "KEY=val\nFOO=bar\n")
    results = strip_comments_envs([p])
    assert results[0].changed is False


def test_strip_comments_envs_multiple_files(tmp_dir):
    """Verify that strip_comments_envs processes multiple files independently."""
    p1 = _write(tmp_dir / ".env.one", "# comment\nKEY=val\n")
    p2 = _write(tmp_dir / ".env.two", "FOO=bar\n")
    results = strip_comments_envs([p1, p2])
    assert len(results) == 2
    changed = [r for r in results if r.changed]
    unchanged = [r for r in results if not r.changed]
    assert len(changed) == 1
    assert len(unchanged) == 1
    assert changed[0].stripped_lines == 1


def test_format_strip_comments_report(tmp_dir):
    p = _write(tmp_dir / ".env", "# hi\nKEY=val\n")
    results = strip_comments_envs([p])
    report = format_strip_comments_report(results)
    assert "changed" in report
    assert "1 comment(s) removed" in report


def test_format_unchanged_report(tmp_dir):
    p = _write(tmp_dir / ".env", "KEY=val\n")
    results = strip_comments_envs([p])
    report = format_strip_comments_report(results)
    assert "unchanged" in report
    assert "0 comment(s) removed" in report
