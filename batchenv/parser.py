"""Parser for .env files."""
from pathlib import Path
from typing import Dict, Optional


def parse_env_file(path: str | Path) -> Dict[str, Optional[str]]:
    """
    Parse a .env file and return a dict of key-value pairs.

    Supports:
    - KEY=VALUE
    - KEY="VALUE" or KEY='VALUE'
    - # comments
    - Empty lines
    - Keys with no value (KEY=)
    """
    env: Dict[str, Optional[str]] = {}
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f".env file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                raise ValueError(
                    f"Invalid line {line_num} in {path}: '{line}' (missing '=')"
                )

            key, _, raw_value = line.partition("=")
            key = key.strip()

            if not key:
                raise ValueError(f"Empty key at line {line_num} in {path}")

            value: Optional[str] = raw_value.strip()

            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            elif value == "":
                value = None

            env[key] = value

    return env


def serialize_env(env: Dict[str, Optional[str]]) -> str:
    """Serialize a dict back to .env file content."""
    lines = []
    for key, value in env.items():
        if value is None:
            lines.append(f"{key}=")
        elif any(c in value for c in (" ", "\t", "#", '"', "'")):
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        else:
            lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n"
