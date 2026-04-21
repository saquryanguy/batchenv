"""Encrypt and decrypt values in .env files using Fernet symmetric encryption."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:  # pragma: no cover
    Fernet = None  # type: ignore
    InvalidToken = Exception  # type: ignore


@dataclass
class EncryptResult:
    path: str
    changed_keys: List[str] = field(default_factory=list)
    skipped_keys: List[str] = field(default_factory=list)
    changed: bool = False


def _require_cryptography() -> None:
    if Fernet is None:
        raise RuntimeError(
            "'cryptography' package is required. Install it with: pip install cryptography"
        )


def generate_key() -> str:
    """Generate and return a new Fernet key as a string."""
    _require_cryptography()
    return Fernet.generate_key().decode()


def encrypt_env(
    env: Dict[str, str],
    key: str,
    keys_to_encrypt: Optional[List[str]] = None,
    prefix: str = "enc:",
) -> EncryptResult:
    """Encrypt values in *env* for the given keys (or all keys if None).
    Already-encrypted values (prefixed) are skipped."""
    _require_cryptography()
    f = Fernet(key.encode() if isinstance(key, str) else key)
    result = EncryptResult(path="")
    targets = keys_to_encrypt if keys_to_encrypt is not None else list(env.keys())
    for k in targets:
        if k not in env:
            result.skipped_keys.append(k)
            continue
        v = env[k]
        if v.startswith(prefix):
            result.skipped_keys.append(k)
            continue
        env[k] = prefix + f.encrypt(v.encode()).decode()
        result.changed_keys.append(k)
    result.changed = bool(result.changed_keys)
    return result


def decrypt_env(
    env: Dict[str, str],
    key: str,
    prefix: str = "enc:",
) -> EncryptResult:
    """Decrypt values in *env* that carry *prefix*."""
    _require_cryptography()
    f = Fernet(key.encode() if isinstance(key, str) else key)
    result = EncryptResult(path="")
    for k, v in env.items():
        if not v.startswith(prefix):
            result.skipped_keys.append(k)
            continue
        try:
            env[k] = f.decrypt(v[len(prefix):].encode()).decode()
            result.changed_keys.append(k)
        except InvalidToken:
            result.skipped_keys.append(k)
    result.changed = bool(result.changed_keys)
    return result


def format_encrypt_report(results: List[EncryptResult], action: str = "encrypt") -> str:
    lines: List[str] = []
    for r in results:
        tag = "changed" if r.changed else "unchanged"
        lines.append(f"{r.path}: [{tag}] {action}ed {len(r.changed_keys)} key(s)")
        for k in r.changed_keys:
            lines.append(f"  ~ {k}")
    return "\n".join(lines)
