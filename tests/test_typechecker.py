"""Tests for batchenv.typechecker."""
import pytest
from batchenv.typechecker import (
    TypeCheckResult,
    TypeIssue,
    _infer_type,
    typecheck_env,
    typecheck_envs,
    format_typecheck_report,
)


# ---------------------------------------------------------------------------
# _infer_type
# ---------------------------------------------------------------------------

def test_infer_empty():
    assert _infer_type("") == "empty"


def test_infer_bool_true():
    assert _infer_type("true") == "bool"
    assert _infer_type("True") == "bool"
    assert _infer_type("1") == "bool"


def test_infer_int():
    assert _infer_type("99999") == "int"
    assert _infer_type("-42") == "int"


def test_infer_port_or_int():
    assert _infer_type("8080") == "port_or_int"
    assert _infer_type("443") == "port_or_int"


def test_infer_float():
    assert _infer_type("3.14") == "float"
    assert _infer_type("-0.5") == "float"


def test_infer_url():
    assert _infer_type("https://example.com") == "url"
    assert _infer_type("http://localhost:8080") == "url"


def test_infer_string():
    assert _infer_type("hello world") == "string"
    assert _infer_type("my-secret-key") == "string"


# ---------------------------------------------------------------------------
# typecheck_env
# ---------------------------------------------------------------------------

def test_no_hints_no_issues():
    env = {"HOST": "localhost", "PORT": "8080", "DEBUG": "true"}
    result = typecheck_env(env, "app.env")
    assert result.ok
    assert result.issues == []


def test_hint_match_passes():
    env = {"PORT": "8080"}
    result = typecheck_env(env, "app.env", hints={"PORT": "port_or_int"})
    assert result.ok


def test_hint_int_accepts_port_or_int():
    env = {"PORT": "3000"}
    result = typecheck_env(env, "app.env", hints={"PORT": "int"})
    assert result.ok  # port_or_int satisfies int hint


def test_hint_mismatch_creates_issue():
    env = {"RETRIES": "three"}
    result = typecheck_env(env, "app.env", hints={"RETRIES": "int"})
    assert not result.ok
    assert len(result.issues) == 1
    issue = result.issues[0]
    assert issue.key == "RETRIES"
    assert issue.expected_type == "int"
    assert issue.actual_type == "string"


def test_empty_value_not_flagged_when_hint_present():
    env = {"SECRET": ""}
    result = typecheck_env(env, "app.env", hints={"SECRET": "string"})
    assert result.ok  # empty is allowed regardless of hint


def test_url_hint_mismatch():
    env = {"CALLBACK": "not-a-url"}
    result = typecheck_env(env, "app.env", hints={"CALLBACK": "url"})
    assert not result.ok
    assert result.issues[0].message.startswith("CALLBACK:")


# ---------------------------------------------------------------------------
# typecheck_envs
# ---------------------------------------------------------------------------

def test_typecheck_envs_multiple_files():
    envs = {
        "a.env": {"PORT": "8080"},
        "b.env": {"PORT": "bad"},
    }
    results = typecheck_envs(envs, hints={"PORT": "int"})
    assert len(results) == 2
    ok_results = [r for r in results if r.ok]
    fail_results = [r for r in results if not r.ok]
    assert len(ok_results) == 1
    assert len(fail_results) == 1


# ---------------------------------------------------------------------------
# format_typecheck_report
# ---------------------------------------------------------------------------

def test_format_report_all_ok():
    results = [TypeCheckResult(file="a.env"), TypeCheckResult(file="b.env")]
    report = format_typecheck_report(results)
    assert "[OK] a.env" in report
    assert "[OK] b.env" in report


def test_format_report_with_issues():
    issue = TypeIssue(
        key="PORT",
        file="app.env",
        expected_type="int",
        actual_type="string",
        value="bad",
        message="PORT: expected int, got string ('bad')",
    )
    result = TypeCheckResult(file="app.env", issues=[issue])
    report = format_typecheck_report([result])
    assert "[FAIL] app.env" in report
    assert "PORT: expected int" in report
