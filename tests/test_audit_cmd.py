from pathlib import Path
import pytest
from batchenv.commands.audit_cmd import run


@pytest.fixture
def tmp_dir(tmp_path):
    return tmp_path


def _write(p: Path, content: str):
    p.write_text(content)


def test_audit_all_ok(tmp_dir, capsys):
    a = tmp_dir / "a.env"
    b = tmp_dir / "b.env"
    _write(a, "FOO=bar\n")
    _write(b, "FOO=bar\n")
    code = run([str(a), str(b)])
    assert code == 0
    out = capsys.readouterr().out
    assert "FOO" in out


def test_audit_missing_file(tmp_dir):
    code = run([str(tmp_dir / "ghost.env")])
    assert code == 1


def test_audit_fail_on_diff(tmp_dir):
    a = tmp_dir / "a.env"
    b = tmp_dir / "b.env"
    _write(a, "FOO=one\n")
    _write(b, "FOO=two\n")
    code = run([str(a), str(b), "--fail-on-diff"])
    assert code == 2


def test_audit_no_fail_on_diff_without_flag(tmp_dir):
    a = tmp_dir / "a.env"
    b = tmp_dir / "b.env"
    _write(a, "FOO=one\n")
    _write(b, "FOO=two\n")
    code = run([str(a), str(b)])
    assert code == 0


def test_audit_fail_on_missing(tmp_dir):
    a = tmp_dir / "a.env"
    b = tmp_dir / "b.env"
    _write(a, "FOO=x\nBAR=y\n")
    _write(b, "FOO=x\n")
    code = run([str(a), str(b), "--fail-on-missing"])
    assert code == 3


def test_audit_output_contains_status(tmp_dir, capsys):
    a = tmp_dir / "a.env"
    b = tmp_dir / "b.env"
    _write(a, "KEY=hello\n")
    _write(b, "KEY=world\n")
    run([str(a), str(b)])
    out = capsys.readouterr().out
    assert "DIFF" in out
