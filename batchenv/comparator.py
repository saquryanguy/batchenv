"""Compare multiple .env files and produce a summary matrix."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class CompareMatrix:
    """Cross-file comparison result."""
    files: List[str]
    all_keys: List[str]
    # matrix[key][file] = value or None if missing
    matrix: Dict[str, Dict[str, Optional[str]]] = field(default_factory=dict)
    common_keys: Set[str] = field(default_factory=set)
    unique_keys: Dict[str, Set[str]] = field(default_factory=dict)  # key -> set of files


def compare_envs(envs: Dict[str, Dict[str, str]]) -> CompareMatrix:
    """Build a comparison matrix across all provided env dicts.

    Args:
        envs: mapping of file path -> parsed env dict

    Returns:
        CompareMatrix with cross-file key/value data
    """
    files = list(envs.keys())
    all_keys: Set[str] = set()
    for env in envs.values():
        all_keys.update(env.keys())

    sorted_keys = sorted(all_keys)
    matrix: Dict[str, Dict[str, Optional[str]]] = {}
    for key in sorted_keys:
        matrix[key] = {f: envs[f].get(key) for f in files}

    # Keys present in every file
    common_keys = {
        key for key in sorted_keys
        if all(envs[f].get(key) is not None for f in files)
    }

    # Keys present in only a subset of files
    unique_keys: Dict[str, Set[str]] = {}
    for key in sorted_keys:
        present_in = {f for f in files if envs[f].get(key) is not None}
        if len(present_in) < len(files):
            unique_keys[key] = present_in

    return CompareMatrix(
        files=files,
        all_keys=sorted_keys,
        matrix=matrix,
        common_keys=common_keys,
        unique_keys=unique_keys,
    )


def format_compare_report(result: CompareMatrix) -> str:
    """Render a human-readable comparison table."""
    if not result.files:
        return "No files to compare."

    lines: List[str] = []
    col_width = 20
    header = "KEY".ljust(col_width) + "".join(f.ljust(col_width) for f in result.files)
    lines.append(header)
    lines.append("-" * len(header))

    for key in result.all_keys:
        row = key.ljust(col_width)
        for f in result.files:
            val = result.matrix[key].get(f)
            cell = "<missing>" if val is None else (val[:17] + "..." if len(val) > 17 else val)
            row += cell.ljust(col_width)
        lines.append(row)

    lines.append("")
    lines.append(f"Common keys : {len(result.common_keys)}")
    lines.append(f"Partial keys: {len(result.unique_keys)}")
    return "\n".join(lines)
