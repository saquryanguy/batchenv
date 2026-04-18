from pathlib import Path
from batchenv.parser import parse_env_file
from batchenv.placeholder import fill_envs


def test_round_trip_fill(tmp_path):
    f = tmp_path / ".env"
    f.write_text("DB_PASS=PLACEHOLDER\nAPP_KEY=\nDEBUG=true\n")
    env = parse_env_file(f)
    results = fill_envs({str(f): env}, {"DB_PASS": "secret", "APP_KEY": "abc123"})
    assert results[0].changed is True
    assert results[0].filled == {"DB_PASS": "secret", "APP_KEY": "abc123"}
    assert "DEBUG" not in results[0].filled


def test_no_placeholders_unchanged(tmp_path):
    f = tmp_path / ".env"
    f.write_text("KEY=value\n")
    env = parse_env_file(f)
    results = fill_envs({str(f): env}, {"KEY": "other"})
    assert results[0].changed is False


def test_multiple_files(tmp_path):
    f1 = tmp_path / "a.env"
    f2 = tmp_path / "b.env"
    f1.write_text("TOKEN=PLACEHOLDER\n")
    f2.write_text("TOKEN=\n")
    envs = {
        str(f1): parse_env_file(f1),
        str(f2): parse_env_file(f2),
    }
    results = fill_envs(envs, {"TOKEN": "tok123"})
    assert all(r.changed for r in results)
    assert all(r.filled["TOKEN"] == "tok123" for r in results)
