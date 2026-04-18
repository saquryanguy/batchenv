# batchenv

> CLI tool to sync and diff `.env` files across multiple project directories

---

## Installation

```bash
pip install batchenv
```

Or with pipx:

```bash
pipx install batchenv
```

---

## Usage

```bash
# Diff .env files across multiple directories
batchenv diff ./project-a ./project-b ./project-c

# Sync a source .env to multiple target directories
batchenv sync ./project-a/.env ./project-b ./project-c

# Check for missing keys across all projects
batchenv check ./project-a ./project-b ./project-c
```

**Example output:**

```
[diff] ./project-b/.env
  + NEW_KEY=value      (missing in source)
  - DB_HOST            (missing in target)

[diff] ./project-c/.env
  ✓ In sync
```

---

## Options

| Flag | Description |
|------|-------------|
| `--dry-run` | Preview changes without writing files |
| `--keys-only` | Compare keys only, ignore values |
| `--output` | Write report to a file |

---

## License

MIT © [batchenv contributors](LICENSE)