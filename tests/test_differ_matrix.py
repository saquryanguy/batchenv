"""Tests for batchenv.differ_matrix."""
from pathlib import Path

import pytest

from batchenv.differ_matrix import (
    DiffMatrixResult,
    PairDiff,
    diff_matrix,
    format_diff_matrix_report,
)
from batchenv.diff import EnvDiff


def _paths(*names: str):
    return [Path(n) for n in names]


def test_no_files_returns_empty_result():
    result = diff_matrix({})
    assert result.pairs == []
    assert not result.any_differences


def test_single_file_no_pairs():
    result = diff_matrix({Path("a.env"): {"K": "v"}})
    assert result.pairs == []


def test_identical_files_no_differences():
    envs = {
        Path("a.env"): {"KEY": "val"},
        Path("b.env"): {"KEY": "val"},
    }
    result = diff_matrix(envs)
    assert len(result.pairs) == 1
    assert not result.pairs[0].has_differences
    assert not result.any_differences


def test_different_files_detected():
    envs = {
        Path("a.env"): {"KEY": "val", "EXTRA": "x"},
        Path("b.env"): {"KEY": "other"},
    }
    result = diff_matrix(envs)
    assert result.any_differences
    pair = result.pairs[0]
    assert "EXTRA" in pair.diff.only_in_source
    assert "KEY" in pair.diff.value_changed


def test_three_files_three_pairs():
    envs = {
        Path("a.env"): {"A": "1"},
        Path("b.env"): {"B": "2"},
        Path("c.env"): {"C": "3"},
    }
    result = diff_matrix(envs)
    assert len(result.pairs) == 3


def test_differing_pairs_filter():
    envs = {
        Path("a.env"): {"K": "same"},
        Path("b.env"): {"K": "same"},
        Path("c.env"): {"K": "different"},
    }
    result = diff_matrix(envs)
    differing = result.differing_pairs
    assert len(differing) == 2


def test_format_no_files():
    result = DiffMatrixResult()
    report = format_diff_matrix_report(result)
    assert "No files" in report


def test_format_identical_pair():
    envs = {
        Path("a.env"): {"K": "v"},
        Path("b.env"): {"K": "v"},
    }
    result = diff_matrix(envs)
    report = format_diff_matrix_report(result)
    assert "identical" in report


def test_format_diff_pair_shows_changes():
    envs = {
        Path("a.env"): {"KEY": "old", "ONLY_A": "x"},
        Path("b.env"): {"KEY": "new", "ONLY_B": "y"},
    }
    result = diff_matrix(envs)
    report = format_diff_matrix_report(result)
    assert "KEY" in report
    assert "ONLY_A" in report
    assert "ONLY_B" in report
    assert "old" in report
    assert "new" in report
