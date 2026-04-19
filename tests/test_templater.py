import pytest
from batchenv.templater import (
    render_template,
    template_envs,
    format_template_report,
    TemplateResult,
)


def test_render_basic_substitution():
    tmpl = "Hello {{NAME}}!"
    result, missing = render_template(tmpl, {"NAME": "World"})
    assert result == "Hello World!"
    assert missing == []


def test_render_multiple_keys():
    tmpl = "{{HOST}}:{{PORT}}"
    result, missing = render_template(tmpl, {"HOST": "localhost", "PORT": "5432"})
    assert result == "localhost:5432"
    assert missing == []


def test_render_missing_key_preserved():
    tmpl = "{{MISSING_KEY}}"
    result, missing = render_template(tmpl, {})
    assert result == "{{MISSING_KEY}}"
    assert "MISSING_KEY" in missing


def test_render_partial_missing():
    tmpl = "{{PRESENT}} and {{ABSENT}}"
    result, missing = render_template(tmpl, {"PRESENT": "yes"})
    assert "yes" in result
    assert "ABSENT" in missing


def test_render_whitespace_in_placeholder():
    tmpl = "{{ KEY }}"
    result, missing = render_template(tmpl, {"KEY": "value"})
    assert result == "value"


def test_template_envs_multiple():
    tmpl = "DB={{DB_NAME}}"
    envs = {
        "a/.env": {"DB_NAME": "alpha"},
        "b/.env": {"DB_NAME": "beta"},
    }
    results = template_envs(tmpl, envs)
    assert len(results) == 2
    rendered = {r.path: r.rendered for r in results}
    assert rendered["a/.env"] == "DB=alpha"
    assert rendered["b/.env"] == "DB=beta"


def test_template_envs_changed_flag():
    tmpl = "{{X}}"
    results = template_envs(tmpl, {"p": {"X": "1"}})
    assert results[0].changed is True


def test_template_envs_no_placeholders():
    tmpl = "no placeholders here"
    results = template_envs(tmpl, {"p": {"X": "1"}})
    assert results[0].changed is False


def test_format_template_report_ok():
    results = [TemplateResult(path="a/.env", rendered="val", missing_keys=[])]
    report = format_template_report(results)
    assert "a/.env: ok" in report


def test_format_template_report_missing():
    results = [TemplateResult(path="b/.env", rendered="", missing_keys=["FOO", "BAR"])]
    report = format_template_report(results)
    assert "FOO" in report
    assert "BAR" in report
