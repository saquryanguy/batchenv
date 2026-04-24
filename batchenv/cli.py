"""Main CLI entry point for batchenv.

Wires all subcommands together via argparse and dispatches to the
appropriate command module.
"""

import argparse
import sys

from batchenv.commands import (
    audit_cmd,
    compare_cmd,
    copy_cmd,
    dedupe_cmd,
    diff_cmd,
    encrypt_cmd,
    export_cmd,
    group_cmd,
    lint_cmd,
    list_cmd,
    merge_cmd,
    placeholder_cmd,
    redact_cmd,
    rename_cmd,
    rename_key_cmd,
    sort_cmd,
    strip_cmd,
    stripcomments_cmd,
    sync_cmd,
    template_cmd,
    trim_cmd,
    validate_cmd,
)


def build_parser() -> argparse.ArgumentParser:
    """Construct the top-level argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        prog="batchenv",
        description="Sync, diff, and manage .env files across multiple project directories.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="<command>")
    subparsers.required = True

    # Register each subcommand.  Commands that expose a register() helper use
    # it; the rest receive a minimal sub-parser and rely on their run() to
    # accept a plain Namespace.
    _add = subparsers.add_parser  # shorthand

    # ------------------------------------------------------------------ #
    # diff
    # ------------------------------------------------------------------ #
    p_diff = _add("diff", help="Show differences between two .env files.")
    p_diff.add_argument("source", help="Reference .env file.")
    p_diff.add_argument("target", help="Target .env file to compare against source.")
    p_diff.set_defaults(func=diff_cmd.run)

    # ------------------------------------------------------------------ #
    # sync
    # ------------------------------------------------------------------ #
    p_sync = _add("sync", help="Sync missing keys from a source .env into target files.")
    p_sync.add_argument("source", help="Source .env file.")
    p_sync.add_argument("targets", nargs="+", help="Target .env files to update.")
    p_sync.add_argument("--dry-run", action="store_true", help="Preview changes without writing.")
    p_sync.add_argument("--fill-value", default="", help="Placeholder value for added keys.")
    p_sync.set_defaults(func=sync_cmd.run)

    # ------------------------------------------------------------------ #
    # list
    # ------------------------------------------------------------------ #
    p_list = _add("list", help="Discover .env files under a directory.")
    p_list.add_argument("directory", help="Root directory to search.")
    p_list.add_argument("--recursive", action="store_true", help="Search recursively.")
    p_list.set_defaults(func=list_cmd.run)

    # ------------------------------------------------------------------ #
    # validate
    # ------------------------------------------------------------------ #
    p_val = _add("validate", help="Validate that .env files contain required keys.")
    p_val.add_argument("reference", help="Reference .env file defining required keys.")
    p_val.add_argument("targets", nargs="+", help="Files to validate.")
    p_val.add_argument("--strict", action="store_true", help="Fail on extra keys too.")
    p_val.set_defaults(func=validate_cmd.run)

    # ------------------------------------------------------------------ #
    # merge
    # ------------------------------------------------------------------ #
    p_merge = _add("merge", help="Merge multiple .env files into one.")
    p_merge.add_argument("sources", nargs="+", help="Source .env files (in priority order).")
    p_merge.add_argument("--output", "-o", required=True, help="Output file path.")
    p_merge.add_argument(
        "--strategy",
        choices=["first", "last", "error"],
        default="first",
        help="Conflict resolution strategy (default: first).",
    )
    p_merge.set_defaults(func=merge_cmd.run)

    # ------------------------------------------------------------------ #
    # export
    # ------------------------------------------------------------------ #
    p_exp = _add("export", help="Export .env files as shell export statements.")
    p_exp.add_argument("sources", nargs="+", help="Source .env files.")
    p_exp.add_argument("--output", "-o", default="-", help="Output file (default: stdout).")
    p_exp.set_defaults(func=export_cmd.run)

    # ------------------------------------------------------------------ #
    # audit
    # ------------------------------------------------------------------ #
    p_audit = _add("audit", help="Audit consistency of keys across .env files.")
    p_audit.add_argument("files", nargs="+", help=".env files to audit.")
    p_audit.add_argument("--fail-on-diff", action="store_true", help="Exit non-zero if issues found.")
    p_audit.set_defaults(func=audit_cmd.run)

    # ------------------------------------------------------------------ #
    # rename  (file-level rename)
    # ------------------------------------------------------------------ #
    p_ren = _add("rename", help="Rename a key across multiple .env files.")
    p_ren.add_argument("old_key", help="Key to rename.")
    p_ren.add_argument("new_key", help="Replacement key name.")
    p_ren.add_argument("files", nargs="+", help=".env files to update.")
    p_ren.add_argument("--dry-run", action="store_true")
    p_ren.set_defaults(func=rename_cmd.run)

    # ------------------------------------------------------------------ #
    # rename-key  (single-file rename)
    # ------------------------------------------------------------------ #
    rename_key_cmd.register(subparsers)

    # ------------------------------------------------------------------ #
    # copy
    # ------------------------------------------------------------------ #
    p_copy = _add("copy", help="Copy a key's value from one .env file to others.")
    p_copy.add_argument("key", help="Key to copy.")
    p_copy.add_argument("source", help="Source .env file.")
    p_copy.add_argument("targets", nargs="+", help="Target .env files.")
    p_copy.add_argument("--overwrite", action="store_true", help="Overwrite existing key in targets.")
    p_copy.set_defaults(func=copy_cmd.run)

    # ------------------------------------------------------------------ #
    # sort
    # ------------------------------------------------------------------ #
    sort_cmd.register(subparsers) if hasattr(sort_cmd, "register") else _register_sort(subparsers)

    # ------------------------------------------------------------------ #
    # trim
    # ------------------------------------------------------------------ #
    trim_cmd.register(subparsers)

    # ------------------------------------------------------------------ #
    # strip  (whitespace)
    # ------------------------------------------------------------------ #
    p_strip = _add("strip", help="Strip leading/trailing whitespace from .env values.")
    p_strip.add_argument("files", nargs="+")
    p_strip.add_argument("--dry-run", action="store_true")
    p_strip.set_defaults(func=strip_cmd.run)

    # ------------------------------------------------------------------ #
    # dedupe
    # ------------------------------------------------------------------ #
    dedupe_cmd.register(subparsers)

    # ------------------------------------------------------------------ #
    # redact
    # ------------------------------------------------------------------ #
    redact_cmd.register(subparsers)

    # ------------------------------------------------------------------ #
    # strip-comments
    # ------------------------------------------------------------------ #
    p_sc = _add("strip-comments", help="Remove comment lines from .env files.")
    p_sc.add_argument("files", nargs="+")
    p_sc.add_argument("--dry-run", action="store_true")
    p_sc.set_defaults(func=stripcomments_cmd.run)

    # ------------------------------------------------------------------ #
    # placeholder
    # ------------------------------------------------------------------ #
    placeholder_cmd.register(subparsers)

    # ------------------------------------------------------------------ #
    # lint
    # ------------------------------------------------------------------ #
    lint_cmd.register(subparsers)

    # ------------------------------------------------------------------ #
    # template
    # ------------------------------------------------------------------ #
    template_cmd.register(subparsers)

    # ------------------------------------------------------------------ #
    # encrypt / decrypt
    # ------------------------------------------------------------------ #
    encrypt_cmd.register(subparsers)

    # ------------------------------------------------------------------ #
    # group
    # ------------------------------------------------------------------ #
    group_cmd.register(subparsers)

    # ------------------------------------------------------------------ #
    # compare
    # ------------------------------------------------------------------ #
    compare_cmd.register(subparsers)

    return parser


def _register_sort(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Fallback sort registration when sort_cmd has no register()."""
    p = subparsers.add_parser("sort", help="Sort keys in .env files alphabetically.")
    p.add_argument("files", nargs="+")
    p.add_argument("--reverse", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=sort_cmd.run)


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch to the selected subcommand.

    Returns the exit code (0 = success, non-zero = failure).
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
        return 0 if result is None else int(result)
    except KeyboardInterrupt:
        print("Aborted.", file=sys.stderr)
        return 130
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
