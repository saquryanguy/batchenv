"""Integration tests for encrypt → decrypt round-trip across multiple files."""
import pytest

pytest.importorskip("cryptography", reason="cryptography not installed")

from batchenv.encryptor import decrypt_env, encrypt_env, generate_key


def test_multiple_files_round_trip():
    key = generate_key()
    envs = [
        {"DB_PASS": "alpha", "API_KEY": "beta"},
        {"DB_PASS": "gamma", "HOST": "localhost"},
    ]
    originals = [dict(e) for e in envs]

    for env in envs:
        encrypt_env(env, key)

    for env, original in zip(envs, originals):
        decrypt_env(env, key)
        assert env == original


def test_selective_encrypt_leaves_others_plain():
    key = generate_key()
    env = {"SECRET": "s3cr3t", "PUBLIC": "open"}
    encrypt_env(env, key, keys_to_encrypt=["SECRET"])
    assert env["PUBLIC"] == "open"
    assert env["SECRET"].startswith("enc:")


def test_wrong_key_skips_on_decrypt():
    key1 = generate_key()
    key2 = generate_key()
    env = {"A": "value"}
    encrypt_env(env, key1)
    result = decrypt_env(env, key2)  # wrong key → skipped
    assert "A" in result.skipped_keys
    assert result.changed is False


def test_idempotent_encryption():
    key = generate_key()
    env = {"X": "data"}
    encrypt_env(env, key)
    first = env["X"]
    encrypt_env(env, key)  # already encrypted — should skip
    assert env["X"] == first
