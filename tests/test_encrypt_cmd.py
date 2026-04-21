"""Tests for batchenv.commands.encrypt_cmd."""
import pytest

pytest.importorskip("cryptography", reason="cryptography not installed")

from pathlib import Path

from batchenv.commands.encrypt_cmd import run
from batchenv.encryptor import generate_key
from batchenv.parser import parse_env_file


@pytest.fixture()
def tmp_dir(tmp_path):
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content)
    return p


@pytest.fixture()
def key() -> str:
    return generate_key()


class _Args:
    def __init__(self, **kw):
        defaults = dict(
            files=[],
            key="",
            generate_key=False,
            decrypt=False,
            keys=None,
            dry_run=False,
        )
        defaults.update(kw)
        self.__dict__.update(defaults)


def test_generate_key_flag(capsys):
    args = _Args(generate_key=True)
    rc = run(args)
    assert rc == 0
    captured = capsys.readouterr()
    assert len(captured.out.strip()) > 0


def test_missing_key_returns_error(capsys):
    args = _Args(files=[], key="")
    rc = run(args)
    assert rc == 1


def test_missing_file_returns_error(tmp_dir, key, capsys):
    args = _Args(files=[str(tmp_dir / "nonexistent.env")], key=key)
    rc = run(args)
    assert rc == 1


def test_encrypt_writes_file(tmp_dir, key):
    f = _write(tmp_dir / ".env", "SECRET=hello\nHOST=localhost\n")
    args = _Args(files=[str(f)], key=key, keys=["SECRET"])
    rc = run(args)
    assert rc == 0
    env = parse_env_file(f)
    assert env["SECRET"].startswith("enc:")
    assert env["HOST"] == "localhost"


def test_dry_run_does_not_modify(tmp_dir, key):
    original = "SECRET=hello\n"
    f = _write(tmp_dir / ".env", original)
    args = _Args(files=[str(f)], key=key, dry_run=True)
    rc = run(args)
    assert rc == 0
    assert f.read_text() == original


def test_decrypt_round_trip(tmp_dir, key):
    f = _write(tmp_dir / ".env", "SECRET=hello\n")
    enc_args = _Args(files=[str(f)], key=key)
    run(enc_args)
    dec_args = _Args(files=[str(f)], key=key, decrypt=True)
    rc = run(dec_args)
    assert rc == 0
    env = parse_env_file(f)
    assert env["SECRET"] == "hello"
