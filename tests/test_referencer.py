"""Tests for batchenv.referencer."""
from pathlib import Path

import pytest

from batchenv.referencer import (
    ReferenceResult,
    _extract_refs,
    find_references,
    missing_references,
    reference_envs,
    format_reference_report,
)


# ---------------------------------------------------------------------------
# unit helpers
# ---------------------------------------------------------------------------

def test_extract_refs_curly_syntax():
    assert _extract_refs("${FOO}") == ["FOO"]


def test_extract_refs_bare_syntax():
    assert _extract_refs("$BAR") == ["BAR"]


def test_extract_refs_mixed():
    refs = _extract_refs("${HOST}:$PORT/db")
    assert refs == ["HOST", "PORT"]


def test_extract_refs_no_refs():
    assert _extract_refs("plain-value") == []


# ---------------------------------------------------------------------------
# find_references
# ---------------------------------------------------------------------------

def test_find_references_basic():
    env = {"URL": "http://${HOST}:${PORT}", "HOST": "localhost", "PORT": "5432"}
    refs = find_references(env)
    assert refs == {"URL": ["HOST", "PORT"]}


def test_find_references_empty_env():
    assert find_references({}) == {}


def test_find_references_no_refs():
    env = {"A": "1", "B": "2"}
    assert find_references(env) == {}


# ---------------------------------------------------------------------------
# missing_references
# ---------------------------------------------------------------------------

def test_missing_references_all_defined():
    env = {"URL": "${HOST}:${PORT}", "HOST": "localhost", "PORT": "5432"}
    assert missing_references(env) == {}


def test_missing_references_detects_absent_key():
    env = {"URL": "${HOST}:${PORT}", "HOST": "localhost"}
    result = missing_references(env)
    assert result == {"URL": ["PORT"]}


def test_missing_references_multiple_missing():
    env = {"DSN": "${USER}:${PASS}@${HOST}"}
    result = missing_references(env)
    assert set(result["DSN"]) == {"USER", "PASS", "HOST"}


# ---------------------------------------------------------------------------
# reference_envs + format_reference_report
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_dir(tmp_path):
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content)
    return p


def test_reference_envs_single_file(tmp_dir):
    f = _write(tmp_dir / ".env", "HOST=localhost\nPORT=5432\nURL=${HOST}:${PORT}\n")
    results = reference_envs([f])
    assert len(results) == 1
    r = results[0]
    assert r.references == {"URL": ["HOST", "PORT"]}
    assert r.missing_refs == {}
    assert r.changed is False


def test_reference_envs_missing_ref(tmp_dir):
    f = _write(tmp_dir / ".env", "URL=${HOST}:${PORT}\n")
    results = reference_envs([f])
    r = results[0]
    assert set(r.missing_refs["URL"]) == {"HOST", "PORT"}
    assert r.changed is True


def test_reference_envs_nonexistent_file(tmp_dir):
    p = tmp_dir / "ghost.env"
    results = reference_envs([p])
    assert results[0].references == {}


def test_format_reference_report_no_refs(tmp_dir):
    f = _write(tmp_dir / ".env", "A=1\nB=2\n")
    results = reference_envs([f])
    report = format_reference_report(results)
    assert "no variable references found" in report


def test_format_reference_report_with_missing(tmp_dir):
    f = _write(tmp_dir / ".env", "URL=${HOST}\n")
    results = reference_envs([f])
    report = format_reference_report(results)
    assert "MISSING" in report
    assert "HOST" in report
