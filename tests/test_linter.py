import pytest
from batchenv.linter import lint_env, lint_envs, format_lint_report, LintIssue


def test_clean_env_no_issues():
    env = {"DATABASE_URL": "postgres://prod-host/db", "DEBUG": "false"}
    result = lint_env(env, path=".env")
    assert result.issues == []
    assert result.ok


def test_lowercase_key_warning():
    env = {"database_url": "postgres://host/db"}
    result = lint_env(env)
    keys_msgs = [(i.key, i.message) for i in result.issues]
    assert any("uppercase" in m for _, m in keys_msgs)


def test_empty_value_warning():
    env = {"API_KEY": ""}
    result = lint_env(env)
    assert any("empty" in i.message.lower() for i in result.issues)


def test_localhost_warning():
    env = {"DB_HOST": "localhost"}
    result = lint_env(env)
    assert any("localhost" in i.message for i in result.issues)


def test_loopback_warning():
    env = {"REDIS_URL": "redis://127.0.0.1:6379"}
    result = lint_env(env)
    assert any("loopback" in i.message for i in result.issues)


def test_placeholder_todo_warning():
    env = {"SECRET_KEY": "todo"}
    result = lint_env(env)
    assert any("todo" in i.message.lower() for i in result.issues)


def test_changeme_warning():
    env = {"ADMIN_PASS": "changeme"}
    result = lint_env(env)
    assert any("changeme" in i.message.lower() for i in result.issues)


def test_example_domain_warning():
    env = {"SITE_URL": "https://example.com"}
    result = lint_env(env)
    assert any("example domain" in i.message for i in result.issues)


def test_lint_envs_multiple():
    envs = {
        ".env.prod": {"API_KEY": "real-key"},
        ".env.dev": {"api_key": "localhost"},
    }
    results = lint_envs(envs)
    assert len(results) == 2
    dev = next(r for r in results if r.path == ".env.dev")
    assert len(dev.issues) >= 2


def test_format_lint_report_ok():
    env = {"PORT": "8080"}
    result = lint_env(env, path=".env")
    report = format_lint_report([result])
    assert "[OK]" in report


def test_format_lint_report_issues():
    env = {"secret": "changeme"}
    result = lint_env(env, path=".env.dev")
    report = format_lint_report([result])
    assert "[LINT]" in report
    assert "WARN" in report
