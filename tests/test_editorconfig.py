from __future__ import annotations

import configparser

import pytest
from typer.testing import CliRunner

from hinagata import cli, prompts
from hinagata.editorconfig import IndentStyle, is_valid_size, render


runner = CliRunner()


def _parse(text: str) -> configparser.ConfigParser:
    # EditorConfig is INI-like; the top-level ``root = true`` needs a section for configparser.
    parser = configparser.ConfigParser()
    parser.read_string("[preamble]\n" + text)
    return parser


def test_default_is_four_spaces() -> None:
    parser = _parse(render())

    assert parser["preamble"]["root"] == "true"
    assert parser["*"]["indent_style"] == "space"
    assert parser["*"]["indent_size"] == "4"
    assert parser["*"]["insert_final_newline"] == "true"


def test_spaces_get_compact_override_for_config_files() -> None:
    parser = _parse(render(IndentStyle.SPACE, 4))

    assert parser["*.{html,css,js,json,sh,yml,yaml,toml}"]["indent_size"] == "2"
    assert parser["Makefile"]["indent_style"] == "tab"


def test_two_spaces_need_no_override() -> None:
    parser = _parse(render(IndentStyle.SPACE, 2))

    assert "*.{html,css,js,json,sh,yml,yaml,toml}" not in parser


def test_tabs_have_no_overrides_besides_markdown() -> None:
    parser = _parse(render(IndentStyle.TAB, 8))

    assert parser["*"]["indent_style"] == "tab"
    assert parser["*"]["indent_size"] == "8"
    assert "Makefile" not in parser
    assert parser["*.md"]["trim_trailing_whitespace"] == "false"


@pytest.mark.parametrize(("value", "valid"), [("4", True), (" 2 ", True), ("0", False), ("17", False), ("x", False)])
def test_is_valid_size(value, valid) -> None:
    assert is_valid_size(value) is valid


def test_writes_file(tmp_path) -> None:
    out = tmp_path / ".editorconfig"

    result = runner.invoke(cli.app, ["editorconfig", "-s", "tab", "-i", "4", "-o", str(out)])

    assert result.exit_code == 0
    assert out.read_text() == render(IndentStyle.TAB, 4)


def test_defaults_without_terminal(tmp_path) -> None:
    out = tmp_path / ".editorconfig"

    result = runner.invoke(cli.app, ["editorconfig", "-o", str(out)])

    assert result.exit_code == 0
    assert out.read_text() == render()


def test_style_ignores_case(tmp_path) -> None:
    out = tmp_path / ".editorconfig"

    result = runner.invoke(cli.app, ["editorconfig", "-s", "TAB", "-o", str(out)])

    assert result.exit_code == 0
    assert "indent_style = tab" in out.read_text()


def test_rejects_unknown_style() -> None:
    result = runner.invoke(cli.app, ["editorconfig", "-s", "spaces"])

    assert result.exit_code == 2


@pytest.mark.parametrize("size", ["0", "17"])
def test_rejects_out_of_range_size(size) -> None:
    result = runner.invoke(cli.app, ["editorconfig", "-i", size])

    assert result.exit_code == 2


def test_stdout_output() -> None:
    result = runner.invoke(cli.app, ["editorconfig", "-o", "-"])

    assert result.exit_code == 0
    assert result.stdout == render()


def test_refuses_to_overwrite(tmp_path) -> None:
    out = tmp_path / ".editorconfig"
    out.write_text("keep me")

    result = runner.invoke(cli.app, ["editorconfig", "-o", str(out)])

    assert result.exit_code == 1
    assert out.read_text() == "keep me"


def test_force_overwrites(tmp_path) -> None:
    out = tmp_path / ".editorconfig"
    out.write_text("replace me")

    result = runner.invoke(cli.app, ["editorconfig", "-f", "-o", str(out)])

    assert result.exit_code == 0
    assert out.read_text() == render()


@pytest.fixture
def terminal(monkeypatch) -> None:
    monkeypatch.setattr(cli, "is_interactive", lambda: True)


@pytest.mark.usefixtures("terminal")
def test_interactive_flow(monkeypatch, tmp_path) -> None:
    out = tmp_path / ".editorconfig"
    asked: dict[str, int] = {}

    def ask_size(default: int) -> int:
        asked["default"] = default
        return 3

    monkeypatch.setattr(prompts, "select_indent_style", lambda: IndentStyle.SPACE)
    monkeypatch.setattr(prompts, "ask_indent_size", ask_size)

    result = runner.invoke(cli.app, ["editorconfig", "-o", str(out)])

    assert result.exit_code == 0
    assert asked["default"] == 4
    assert out.read_text() == render(IndentStyle.SPACE, 3)


@pytest.mark.usefixtures("terminal")
def test_interactive_skips_prompts_for_given_flags(monkeypatch, tmp_path) -> None:
    out = tmp_path / ".editorconfig"

    def fail(*_args) -> None:
        raise AssertionError

    monkeypatch.setattr(prompts, "select_indent_style", fail)
    monkeypatch.setattr(prompts, "ask_indent_size", fail)

    result = runner.invoke(cli.app, ["editorconfig", "-s", "tab", "-i", "2", "-o", str(out)])

    assert result.exit_code == 0
    assert out.read_text() == render(IndentStyle.TAB, 2)
