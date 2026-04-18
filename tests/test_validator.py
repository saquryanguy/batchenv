"""Tests for batchenv.validator."""
from pathlib import Path

import pytest

from batchenv.validator import ValidationResult, validate_envs, format_validation_report

REF = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}


def _path(name: str) -> Path:
    return Path(f"/fake/{name}")


# ---------------------------------------------------------------------------
# validate_envs
# ---------------------------------------------------------------------------

def test_all_keys_present():
    targets = {_path(".env"): dict(REF)}
    results = validate_envs(REF, targets)
    assert results[_path(".env")].is_valid


def test_missing_keys_detected():
    targets = {_path(".env"): {"HOST": "localhost"}}
    results = validate_envs(REF, targets)
    r = results[_path(".env")]
    assert set(r.missing_keys) == {"PORT", "DEBUG"}
    assert r.extra_keys == []


def test_extra_keys_ignored_by_default():
    targets = {_path(".env"): {**REF, "EXTRA": "val"}}
    results = validate_envs(REF, targets)
    assert results[_path(".env")].is_valid


def test_extra_keys_reported_in_strict_mode():
    targets = {_path(".env"): {**REF, "EXTRA": "val"}}
    results = validate_envs(REF, targets, strict=True)
    r = results[_path(".env")]
    assert r.extra_keys == ["EXTRA"]
    assert r.missing_keys == []


def test_multiple_targets():
    t1 = {_path("a/.env"): dict(REF)}
    t2 = {_path("b/.env"): {"HOST": "x"}}
    targets = {**t1, **t2}
    results = validate_envs(REF, targets)
    assert results[_path("a/.env")].is_valid
    assert not results[_path("b/.env")].is_valid


# ---------------------------------------------------------------------------
# format_validation_report
# ---------------------------------------------------------------------------

def test_format_valid():
    results = {_path(".env"): ValidationResult(path=_path(".env"))}
    report = format_validation_report(results)
    assert "✔" in report
    assert str(_path(".env")) in report


def test_format_invalid_shows_keys():
    r = ValidationResult(path=_path(".env"), missing_keys=["PORT"], extra_keys=["EXTRA"])
    report = format_validation_report({_path(".env"): r})
    assert "missing" in report
    assert "PORT" in report
    assert "extra" in report
    assert "EXTRA" in report
