"""Tests for batchenv.parser module."""
import pytest
from pathlib import Path
from batchenv.parser import parse_env_file, serialize_env


@pytest.fixture
def tmp_env(tmp_path):
    def _write(content: str) -> Path:
        p = tmp_path / ".env"
        p.write_text(content, encoding="utf-8")
        return p
    return _write


def test_basic_key_value(tmp_env):
    p = tmp_env("KEY=value\nFOO=bar\n")
    result = parse_env_file(p)
    assert result == {"KEY": "value", "FOO": "bar"}


def test_quoted_double(tmp_env):
    p = tmp_env('DB_URL="postgres://localhost/db"\n')
    assert parse_env_file(p)["DB_URL"] == "postgres://localhost/db"


def test_quoted_single(tmp_env):
    p = tmp_env("SECRET='my secret'\n")
    assert parse_env_file(p)["SECRET"] == "my secret"


def test_empty_value(tmp_env):
    p = tmp_env("EMPTY=\n")
    assert parse_env_file(p)["EMPTY"] is None


def test_comments_and_blank_lines(tmp_env):
    p = tmp_env("# comment\n\nKEY=val\n")
    assert parse_env_file(p) == {"KEY": "val"}


def test_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        parse_env_file(tmp_path / "missing.env")


def test_invalid_line_no_equals(tmp_env):
    p = tmp_env("BADLINE\n")
    with pytest.raises(ValueError, match="missing '='"):
        parse_env_file(p)


def test_empty_key(tmp_env):
    p = tmp_env("=value\n")
    with pytest.raises(ValueError, match="Empty key"):
        parse_env_file(p)


def test_serialize_basic():
    env = {"A": "1", "B": "hello"}
    assert serialize_env(env) == "A=1\nB=hello\n"


def test_serialize_none_value():
    assert "KEY=\n" in serialize_env({"KEY": None})


def test_serialize_value_with_spaces():
    result = serialize_env({"MSG": "hello world"})
    assert result == 'MSG="hello world"\n'


def test_roundtrip(tmp_env):
    original = {"HOST": "localhost", "PORT": "5432", "PASS": None}
    content = serialize_env(original)
    p = tmp_env(content)
    parsed = parse_env_file(p)
    assert parsed == original
