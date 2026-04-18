import pytest
from batchenv.merger import merge_envs, MergeStrategy, MergeResult


def test_no_conflicts():
    sources = [
        ("a.env", {"FOO": "1", "BAR": "2"}),
        ("b.env", {"BAZ": "3"}),
    ]
    result = merge_envs(sources)
    assert result.merged == {"FOO": "1", "BAR": "2", "BAZ": "3"}
    assert result.conflicts == []


def test_conflict_first_strategy():
    sources = [
        ("a.env", {"FOO": "alpha"}),
        ("b.env", {"FOO": "beta"}),
    ]
    result = merge_envs(sources, MergeStrategy.FIRST)
    assert result.merged["FOO"] == "alpha"
    assert len(result.conflicts) == 1
    assert result.conflicts[0].key == "FOO"


def test_conflict_last_strategy():
    sources = [
        ("a.env", {"FOO": "alpha"}),
        ("b.env", {"FOO": "beta"}),
    ]
    result = merge_envs(sources, MergeStrategy.LAST)
    assert result.merged["FOO"] == "beta"


def test_conflict_error_strategy():
    sources = [
        ("a.env", {"KEY": "x"}),
        ("b.env", {"KEY": "y"}),
    ]
    with pytest.raises(ValueError, match="Conflict on key 'KEY'"):
        merge_envs(sources, MergeStrategy.ERROR)


def test_same_value_no_conflict():
    sources = [
        ("a.env", {"FOO": "same"}),
        ("b.env", {"FOO": "same"}),
    ]
    result = merge_envs(sources)
    assert result.merged["FOO"] == "same"
    assert result.conflicts == []


def test_empty_sources():
    result = merge_envs([])
    assert result.merged == {}
    assert result.conflicts == []


def test_format_merge_report_no_conflicts():
    from batchenv.merger import format_merge_report
    result = MergeResult(merged={"A": "1", "B": "2"}, conflicts=[])
    report = format_merge_report(result)
    assert "No conflicts" in report
    assert "2" in report


def test_format_merge_report_with_conflicts():
    from batchenv.merger import MergeConflict, format_merge_report
    conflict = MergeConflict(key="FOO", values=[("a.env", "x"), ("b.env", "y")])
    result = MergeResult(merged={"FOO": "x"}, conflicts=[conflict])
    report = format_merge_report(result)
    assert "FOO" in report
    assert "a.env" in report
    assert "b.env" in report
