"""Find keys that reference other keys via ${VAR} or $VAR syntax."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set

from batchenv.parser import parse_env_file

_REF_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class ReferenceResult:
    path: Path
    references: Dict[str, List[str]] = field(default_factory=dict)  # key -> [refs]
    missing_refs: Dict[str, List[str]] = field(default_factory=dict)  # key -> [unresolved]
    changed: bool = False


def _extract_refs(value: str) -> List[str]:
    """Return all variable names referenced in *value*."""
    refs: List[str] = []
    for m in _REF_RE.finditer(value):
        refs.append(m.group(1) or m.group(2))
    return refs


def find_references(env: Dict[str, str]) -> Dict[str, List[str]]:
    """Map each key to the list of keys it references."""
    return {k: _extract_refs(v) for k, v in env.items() if _extract_refs(v)}


def missing_references(env: Dict[str, str]) -> Dict[str, List[str]]:
    """Return keys whose referenced variables are absent from *env*."""
    defined: Set[str] = set(env.keys())
    result: Dict[str, List[str]] = {}
    for key, refs in find_references(env).items():
        absent = [r for r in refs if r not in defined]
        if absent:
            result[key] = absent
    return result


def reference_envs(paths: List[Path]) -> List[ReferenceResult]:
    results: List[ReferenceResult] = []
    for p in paths:
        if not p.exists():
            results.append(ReferenceResult(path=p))
            continue
        env = parse_env_file(p)
        refs = find_references(env)
        missing = missing_references(env)
        results.append(
            ReferenceResult(
                path=p,
                references=refs,
                missing_refs=missing,
                changed=bool(missing),
            )
        )
    return results


def format_reference_report(results: List[ReferenceResult]) -> str:
    lines: List[str] = []
    for r in results:
        lines.append(f"[{r.path}]")
        if not r.references:
            lines.append("  no variable references found")
        else:
            for key, refs in r.references.items():
                status = " (MISSING: " + ", ".join(r.missing_refs.get(key, [])) + ")" if key in r.missing_refs else ""
                lines.append(f"  {key} -> {', '.join(refs)}{status}")
    return "\n".join(lines)
