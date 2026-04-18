import pytest
from batchenv.sorter import sort_env, sort_envs, format_sort_report


def test_sort_env_basic():
    env = {"ZEBRA": "1", "APPLE": "2", "MANGO": "3"}
    result = sort_env(env)
    assert list(result.keys()) == ["APPLE", "MANGO", "ZEBRA"]


def test_sort_env_reverse():
    env = {"APPLE": "1", "ZEBRA": "2", "MANGO": "3"}
    result = sort_env(env, reverse=True)
    assert list(result.keys()) == ["ZEBRA", "MANGO", "APPLE"]


def test_sort_env_already_sorted():
    env = {"A": "1", "B": "2", "C": "3"}
    result = sort_env(env)
    assert list(result.keys()) == ["A", "B", "C"]


def test_sort_envs_changed_flag():
    envs = [("a.env", {"Z": "1", "A": "2"})]
    results = sort_envs(envs)
    assert results[0].changed is True


def test_sort_envs_unchanged_flag():
    envs = [("a.env", {"A": "1", "Z": "2"})]
    results = sort_envs(envs)
    assert results[0].changed is False


def test_sort_envs_values_preserved():
    env = {"Z": "zval", "A": "aval"}
    results = sort_envs([("f.env", env)])
    assert results[0].sorted_env["A"] == "aval"
    assert results[0].sorted_env["Z"] == "zval"


def test_format_sort_report_changed():
    envs = [("x.env", {"B": "1", "A": "2"})]
    results = sort_envs(envs)
    report = format_sort_report(results)
    assert "sorted" in report
    assert "x.env" in report


def test_format_sort_report_unchanged():
    envs = [("x.env", {"A": "1", "B": "2"})]
    results = sort_envs(envs)
    report = format_sort_report(results)
    assert "unchanged" in report
