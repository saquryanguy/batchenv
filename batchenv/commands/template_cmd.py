import argparse
from pathlib import Path
from batchenv.parser import parse_env_file
from batchenv.templater import render_template, format_template_report, TemplateResult


def run(args: argparse.Namespace) -> int:
    template_path = Path(args.template)
    if not template_path.exists():
        print(f"Error: template file not found: {template_path}")
        return 1

    template = template_path.read_text()

    env_files = [Path(p) for p in args.env_files]
    missing_files = [p for p in env_files if not p.exists()]
    if missing_files:
        for p in missing_files:
            print(f"Error: env file not found: {p}")
        return 1

    results = []
    for env_path in env_files:
        env = parse_env_file(str(env_path))
        rendered, missing = render_template(template, env)
        results.append(TemplateResult(
            path=str(env_path),
            rendered=rendered,
            missing_keys=missing,
            changed=rendered != template,
        ))

    if args.output_dir:
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        for r, env_path in zip(results, env_files):
            out_file = out_dir / env_path.name
            if not args.dry_run:
                out_file.write_text(r.rendered)
            print(f"{'[dry-run] ' if args.dry_run else ''}wrote {out_file}")
    else:
        for r in results:
            print(f"# {r.path}")
            print(r.rendered)

    print(format_template_report(results))
    has_missing = any(r.missing_keys for r in results)
    return 1 if has_missing else 0


def register(subparsers):
    p = subparsers.add_parser("template", help="Render a template using .env values")
    p.add_argument("template", help="Path to template file with {{KEY}} placeholders")
    p.add_argument("env_files", nargs="+", help="One or more .env files")
    p.add_argument("--output-dir", help="Directory to write rendered files")
    p.add_argument("--dry-run", action="store_true", help="Do not write files")
    p.set_defaults(func=run)
