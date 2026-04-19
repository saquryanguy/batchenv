from dataclasses import dataclass, field
from typing import Dict, List
import re


@dataclass
class TemplateResult:
    path: str
    rendered: str
    missing_keys: List[str] = field(default_factory=list)
    changed: bool = False


def render_template(template: str, env: Dict[str, str]) -> tuple[str, List[str]]:
    """Replace {{KEY}} placeholders with values from env dict."""
    missing: List[str] = []
    pattern = re.compile(r"\{\{\s*(\w+)\s*\}\}")

    def replacer(match: re.Match) -> str:
        key = match.group(1)
        if key in env:
            return env[key]
        missing.append(key)
        return match.group(0)

    rendered = pattern.sub(replacer, template)
    return rendered, missing


def template_envs(
    template: str,
    envs: Dict[str, Dict[str, str]],
) -> List[TemplateResult]:
    results = []
    for path, env in envs.items():
        rendered, missing = render_template(template, env)
        results.append(
            TemplateResult(
                path=path,
                rendered=rendered,
                missing_keys=missing,
                changed=rendered != template,
            )
        )
    return results


def format_template_report(results: List[TemplateResult]) -> str:
    lines = []
    for r in results:
        status = "ok" if not r.missing_keys else f"missing: {', '.join(r.missing_keys)}"
        lines.append(f"{r.path}: {status}")
    return "\n".join(lines)
