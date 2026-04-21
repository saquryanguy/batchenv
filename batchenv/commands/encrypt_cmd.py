"""CLI command: encrypt / decrypt values in .env files."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from batchenv.encryptor import (
    decrypt_env,
    encrypt_env,
    format_encrypt_report,
    generate_key,
)
from batchenv.parser import parse_env_file, serialize_env


def run(args: argparse.Namespace) -> int:
    if args.generate_key:
        print(generate_key())
        return 0

    if not args.key:
        print("error: --key is required (or use --generate-key)")
        return 1

    paths: List[Path] = [Path(p) for p in args.files]
    missing = [p for p in paths if not p.exists()]
    if missing:
        for p in missing:
            print(f"error: file not found: {p}")
        return 1

    action = "decrypt" if args.decrypt else "encrypt"
    results = []

    for path in paths:
        env = parse_env_file(path)
        if action == "encrypt":
            result = encrypt_env(
                env,
                args.key,
                keys_to_encrypt=args.keys if args.keys else None,
            )
        else:
            result = decrypt_env(env, args.key)

        result.path = str(path)

        if not args.dry_run and result.changed:
            path.write_text(serialize_env(env))

        results.append(result)

    print(format_encrypt_report(results, action=action))
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("encrypt", help="Encrypt or decrypt values in .env files")
    p.add_argument("files", nargs="*", help=".env files to process")
    p.add_argument("--key", default="", help="Fernet encryption key")
    p.add_argument("--generate-key", action="store_true", help="Print a new key and exit")
    p.add_argument("--decrypt", action="store_true", help="Decrypt instead of encrypt")
    p.add_argument("--keys", nargs="+", metavar="KEY", help="Specific env keys to encrypt")
    p.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    p.set_defaults(func=run)
