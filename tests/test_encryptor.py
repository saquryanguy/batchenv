"""Tests for batchenv.encryptor."""
import pytest

pytest.importorskip("cryptography", reason="cryptography not installed")

from batchenv.encryptor import (
    EncryptResult,
    decrypt_env,
    encrypt_env,
    format_encrypt_report,
    generate_key,
)


@pytest.fixture()
def key() -> str:
    return generate_key()


def test_generate_key_returns_string(key):
    assert isinstance(key, str)
    assert len(key) > 0


def test_encrypt_env_basic(key):
    env = {"DB_PASS": "secret", "HOST": "localhost"}
    result = encrypt_env(env, key, keys_to_encrypt=["DB_PASS"])
    assert result.changed is True
    assert "DB_PASS" in result.changed_keys
    assert env["DB_PASS"].startswith("enc:")
    assert env["HOST"] == "localhost"  # untouched


def test_encrypt_all_keys_when_none_specified(key):
    env = {"A": "1", "B": "2"}
    result = encrypt_env(env, key)
    assert set(result.changed_keys) == {"A", "B"}
    assert env["A"].startswith("enc:")
    assert env["B"].startswith("enc:")


def test_encrypt_skips_already_encrypted(key):
    env = {"A": "1"}
    encrypt_env(env, key)  # first pass
    already = env["A"]
    result = encrypt_env(env, key)  # second pass — should skip
    assert "A" in result.skipped_keys
    assert env["A"] == already


def test_encrypt_skips_missing_key(key):
    env = {"A": "1"}
    result = encrypt_env(env, key, keys_to_encrypt=["MISSING"])
    assert "MISSING" in result.skipped_keys
    assert result.changed is False


def test_decrypt_env_basic(key):
    env = {"DB_PASS": "secret", "HOST": "localhost"}
    encrypt_env(env, key, keys_to_encrypt=["DB_PASS"])
    result = decrypt_env(env, key)
    assert result.changed is True
    assert env["DB_PASS"] == "secret"
    assert "HOST" in result.skipped_keys


def test_decrypt_skips_plain_values(key):
    env = {"A": "plain"}
    result = decrypt_env(env, key)
    assert result.changed is False
    assert "A" in result.skipped_keys
    assert env["A"] == "plain"


def test_round_trip(key):
    original = {"SECRET": "my_password", "OTHER": "value"}
    env = dict(original)
    encrypt_env(env, key)
    decrypt_env(env, key)
    assert env == original


def test_format_encrypt_report(key):
    r = EncryptResult(path=".env", changed_keys=["A", "B"], changed=True)
    report = format_encrypt_report([r])
    assert ".env" in report
    assert "~ A" in report
    assert "~ B" in report
