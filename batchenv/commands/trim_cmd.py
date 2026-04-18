from pathlib import Path
from batchenv.parser import parse_env_file, serialize_env
from batchenv.trimmer import trim_envs, format_trim_report


def run(args):
    paths = [Path(p) for p in args.files]
    reference_path = Path(args.reference)

    missing = [p for p in paths + [reference_path] if not p.exists()]
    if missing:
        for m in missing:
            print(f"[error] File not found: {m}")
        return 1

    reference = parse_env_file(reference_path)
    envs = {p: parse_env_file(p) for p in paths}

    results = trim_envs(envs, reference)

    if args.dry_run:
        print(format_trim_report(results))
        return 0

    changed = 0
    for path, result in results.items():
        if result.changed:
            path.write_text(serialize_env(result.env))
            changed += 1

    print(format_trim_report(results))
    if args.verbose:
        print(f"{changed} file(s) updated.")
    return 0


def register(subparsers):
    p = subparsers.add_parser("trim", help="Remove keys not present in reference file")
    p.add_argument("reference", help="Reference .env file")
    p.add_argument("files", nargs="+", help="Target .env files to trim")
    p.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    p.add_argument("--verbose", action="store_true", help="Show summary after trimming")
    p.set_defaults(func=run)
