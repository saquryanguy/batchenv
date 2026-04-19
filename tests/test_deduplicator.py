import pytest
from batchenv.deduplicator import dedupe_env, dedupe_envs, format_dedupe_report


def _env(pairs):
    return dict(pairs)


def test_no_duplicates():
    env = {"A": "1", "B": "2"}
    raw = ["A=1\n", "B=2\n"]
    result = dedupe_env("test.env", env, raw)
    assert not result.changed
    assert result.removed_duplicates == []


def test_duplicate_key_detected():
    env = {"A": "2"}  # parser keeps last
    raw = ["A=1\n", "A=2\n"]
    result = dedupe_env("test.env", env, raw)
    assert result.changed
    assert len(result.removed_duplicates) == 1
    assert result.removed_duplicates[0][0] == "A"
    assert result.removed_duplicates[0][1] == "1"


def test_multiple_duplicates():
    env = {"X": "3"}
    raw = ["X=1\n", "X=2\n", "X=3\n"]
    result = dedupe_env("f.env", env, raw)
    assert result.changed
    assert len(result.removed_duplicates) == 2


def test_comments_ignored():
    env = {"A": "1"}
    raw = ["# comment\n", "A=1\n"]
    result = dedupe_env("f.env", env, raw)
    assert not result.changed


def test_dedupe_envs_multiple():
    envs = [{"A": "2"}, {"B": "1"}]
    raws = [["A=1\n", "A=2\n"], ["B=1\n"]]
    paths = ["a.env", "b.env"]
    results = dedupe_envs(paths, envs, raws)
    assert len(results) == 2
    assert results[0].changed
    assert not results[1].changed


def test_format_report_with_duplicates():
    env = {"A": "2"}
    raw = ["A=1\n", "A=2\n"]
    result = dedupe_env("test.env", env, raw)
    report = format_dedupe_report([result])
    assert "test.env" in report
    assert "A=1" in report


def test_format_report_no_duplicates():
    env = {"A": "1"}
    raw = ["A=1\n"]
    result = dedupe_env("clean.env", env, raw)
    report = format_dedupe_report([result])
    assert "no duplicates" in report


def test_format_report_multiple_files():
    """Report should include entries for all files, changed or not."""
    env_changed = {"A": "2"}
    raw_changed = ["A=1\n", "A=2\n"]
    env_clean = {"B": "1"}
    raw_clean = ["B=1\n"]
    results = [
        dedupe_env("dirty.env", env_changed, raw_changed),
        dedupe_env("clean.env", env_clean, raw_clean),
    ]
    report = format_dedupe_report(results)
    assert "dirty.env" in report
    assert "clean.env" in report
