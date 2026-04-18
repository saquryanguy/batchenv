import pytest
from batchenv.trimmer import trim_env, trim_envs, format_trim_report, TrimResult


def test_trim_removes_extra_keys():
    env = {"A": "1", "B": "2", "C": "3"}
    ref = {"A": "x", "B": "y"}
    result = trim_env("test.env", env, ref)
    assert result.trimmed == {"A": "1", "B": "2"}
    assert result.removed_keys == ["C"]
    assert result.changed is True


def test_trim_no_extra_keys():
    env = {"A": "1", "B": "2"}
    ref = {"A": "x", "B": "y", "C": "z"}
    result = trim_env("test.env", env, ref)
    assert result.trimmed == {"A": "1", "B": "2"}
    assert result.removed_keys == []
    assert result.changed is False


def test_trim_empty_env():
    result = trim_env("test.env", {}, {"A": "1"})
    assert result.trimmed == {}
    assert result.changed is False


def test_trim_empty_reference():
    env = {"A": "1", "B": "2"}
    result = trim_env("test.env", env, {})
    assert result.trimmed == {}
    assert set(result.removed_keys) == {"A", "B"}
    assert result.changed is True


def test_trim_envs_multiple():
    envs = {
        "a.env": {"X": "1", "Y": "2"},
        "b.env": {"X": "3", "Z": "4"},
    }
    ref = {"X": "0"}
    results = trim_envs(envs, ref)
    assert len(results) == 2
    paths = {r.path for r in results}
    assert paths == {"a.env", "b.env"}
    for r in results:
        assert "X" in r.trimmed


def test_format_trim_report_changed():
    results = [
        TrimResult(path="a.env", original={}, trimmed={}, removed_keys=["OLD"], changed=True),
        TrimResult(path="b.env", original={}, trimmed={}, removed_keys=[], changed=False),
    ]
    report = format_trim_report(results)
    assert "a.env: removed 1 key(s): OLD" in report
    assert "b.env: no changes" in report


def test_format_trim_report_no_changes():
    results = [
        TrimResult(path="x.env", original={}, trimmed={}, removed_keys=[], changed=False),
    ]
    report = format_trim_report(results)
    assert "no changes" in report
