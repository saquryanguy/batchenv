"""Tests for batchenv.substitutor."""
import pytest
from batchenv.substitutor import (
    substitute_env,
    substitute_envs,
    format_substitute_report,
)


def test_substitute_basic_value():
    env = {"DB_HOST": "localhost", "CACHE_HOST": "localhost", "APP_ENV": "dev"}
    result = substitute_env(env, {"localhost": "prod-db.internal"})
    assert result.updated["DB_HOST"] == "prod-db.internal"
    assert result.updated["CACHE_HOST"] == "prod-db.internal"
    assert result.updated["APP_ENV"] == "dev"
    assert result.changed is True
    assert len(result.substitutions) == 2


def test_substitute_no_match():
    env = {"DB_HOST": "remotehost", "PORT": "5432"}
    result = substitute_env(env, {"localhost": "prod-db.internal"})
    assert result.updated == env
    assert result.changed is False
    assert result.substitutions == []


def test_substitute_scoped_to_keys():
    env = {"DB_HOST": "localhost", "REDIS_HOST": "localhost"}
    result = substitute_env(env, {"localhost": "new-host"}, keys=["DB_HOST"])
    assert result.updated["DB_HOST"] == "new-host"
    assert result.updated["REDIS_HOST"] == "localhost"
    assert len(result.substitutions) == 1


def test_substitute_scoped_key_missing():
    env = {"PORT": "5432"}
    result = substitute_env(env, {"5432": "3306"}, keys=["MISSING_KEY"])
    assert result.updated == env
    assert result.changed is False


def test_substitute_does_not_mutate_original():
    env = {"HOST": "localhost"}
    result = substitute_env(env, {"localhost": "other"})
    assert env["HOST"] == "localhost"
    assert result.original["HOST"] == "localhost"
    assert result.updated["HOST"] == "other"


def test_substitute_multiple_replacements():
    env = {"A": "foo", "B": "bar", "C": "baz"}
    result = substitute_env(env, {"foo": "FOO", "bar": "BAR"})
    assert result.updated["A"] == "FOO"
    assert result.updated["B"] == "BAR"
    assert result.updated["C"] == "baz"
    assert len(result.substitutions) == 2


def test_substitute_envs_sets_path():
    envs = {
        ".env.staging": {"HOST": "localhost"},
        ".env.prod": {"HOST": "prod-host"},
    }
    results = substitute_envs(envs, {"localhost": "staging-db"})
    paths = {r.path for r in results}
    assert ".env.staging" in paths
    assert ".env.prod" in paths
    staging = next(r for r in results if r.path == ".env.staging")
    assert staging.changed is True
    prod = next(r for r in results if r.path == ".env.prod")
    assert prod.changed is False


def test_format_substitute_report_changed():
    env = {"HOST": "localhost"}
    result = substitute_env(env, {"localhost": "newhost"})
    result.path = ".env"
    report = format_substitute_report([result])
    assert ".env" in report
    assert "1 substitution" in report
    assert "localhost" in report
    assert "newhost" in report


def test_format_substitute_report_no_changes():
    env = {"HOST": "remotehost"}
    result = substitute_env(env, {"localhost": "newhost"})
    result.path = ".env"
    report = format_substitute_report([result])
    assert "no changes" in report
