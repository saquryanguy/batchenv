import pytest
from batchenv.redactor import (
    redact_env,
    redact_envs,
    format_redact_report,
    DEFAULT_PATTERNS,
)


def test_redacts_password_key():
    env = {"DB_PASSWORD": "secret123", "HOST": "localhost"}
    result = redact_env("a.env", env)
    assert result.redacted["DB_PASSWORD"] == "***"
    assert result.redacted["HOST"] == "localhost"
    assert "DB_PASSWORD" in result.redacted_keys


def test_redacts_token_key():
    env = {"API_TOKEN": "abc", "PORT": "8080"}
    result = redact_env("a.env", env)
    assert result.redacted["API_TOKEN"] == "***"
    assert result.redacted["PORT"] == "8080"


def test_no_sensitive_keys():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = redact_env("a.env", env)
    assert result.redacted_keys == []
    assert result.redacted == env


def test_custom_placeholder():
    env = {"SECRET_KEY": "val"}
    result = redact_env("a.env", env, placeholder="<hidden>")
    assert result.redacted["SECRET_KEY"] == "<hidden>"


def test_custom_patterns():
    env = {"INTERNAL_CODE": "xyz", "NAME": "app"}
    result = redact_env("a.env", env, patterns={"CODE"})
    assert result.redacted["INTERNAL_CODE"] == "***"
    assert result.redacted["NAME"] == "app"


def test_redact_envs_multiple():
    envs = {
        "a.env": {"DB_PASSWORD": "p", "HOST": "h"},
        "b.env": {"NAME": "app"},
    }
    results = redact_envs(envs)
    assert len(results) == 2
    paths = [r.path for r in results]
    assert "a.env" in paths
    assert "b.env" in paths


def test_format_redact_report_with_redactions():
    env = {"API_SECRET": "x", "HOST": "h"}
    result = redact_env("prod.env", env)
    report = format_redact_report([result])
    assert "prod.env" in report
    assert "API_SECRET" in report


def test_format_redact_report_nothing_to_redact():
    env = {"HOST": "localhost"}
    result = redact_env("dev.env", env)
    report = format_redact_report([result])
    assert "nothing to redact" in report
