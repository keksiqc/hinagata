from __future__ import annotations

import pytest
import typer
from typer.testing import CliRunner

from hinagata import cli, gitignore, prompts
from hinagata.licenses import LICENSES, find


runner = CliRunner()


@pytest.fixture(autouse=True)
def _fixed_author(monkeypatch) -> None:
    monkeypatch.setattr(cli, "default_author", lambda: "Git User")


def test_version() -> None:
    result = runner.invoke(cli.app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip()


def test_no_command_without_terminal_shows_help() -> None:
    result = runner.invoke(cli.app, [])

    assert result.exit_code == 0
    assert "license" in result.stdout
    assert "gitignore" in result.stdout


def test_list_shows_every_license() -> None:
    result = runner.invoke(cli.app, ["license", "--list"])

    assert result.exit_code == 0
    for lic in LICENSES:
        assert lic.spdx_id in result.stdout


def test_writes_license_file(tmp_path) -> None:
    out = tmp_path / "LICENSE"

    result = runner.invoke(cli.app, ["license", "mit", "-a", "Ada Lovelace", "-y", "1843", "-o", str(out)])

    assert result.exit_code == 0
    assert "Copyright (c) 1843 Ada Lovelace" in out.read_text()


def test_defaults_author_and_current_year(tmp_path) -> None:
    out = tmp_path / "LICENSE"

    result = runner.invoke(cli.app, ["license", "MIT", "-o", str(out)])

    assert result.exit_code == 0
    assert "Git User" in out.read_text()
    assert "[year]" not in out.read_text()


def test_stdout_output() -> None:
    result = runner.invoke(cli.app, ["license", "isc", "-a", "Ada", "-y", "2026", "-o", "-"])

    assert result.exit_code == 0
    assert "Copyright (c) 2026 Ada" in result.stdout


def test_license_without_holder_is_verbatim(tmp_path) -> None:
    out = tmp_path / "LICENSE"

    result = runner.invoke(cli.app, ["license", "GPL-3.0", "-o", str(out)])

    lic = find("GPL-3.0")
    assert lic is not None
    assert result.exit_code == 0
    assert out.read_text() == lic.text


def test_unknown_license_suggests_match() -> None:
    result = runner.invoke(cli.app, ["license", "mitt"])

    assert result.exit_code == 2
    assert "Did you mean MIT?" in result.output


def test_invalid_year() -> None:
    result = runner.invoke(cli.app, ["license", "mit", "-y", "last year"])

    assert result.exit_code == 2


def test_missing_license_without_terminal() -> None:
    result = runner.invoke(cli.app, ["license"])

    assert result.exit_code == 2


def test_refuses_to_overwrite(tmp_path) -> None:
    out = tmp_path / "LICENSE"
    out.write_text("keep me")

    result = runner.invoke(cli.app, ["license", "mit", "-o", str(out)])

    assert result.exit_code == 1
    assert out.read_text() == "keep me"


def test_force_overwrites(tmp_path) -> None:
    out = tmp_path / "LICENSE"
    out.write_text("replace me")

    result = runner.invoke(cli.app, ["license", "mit", "-f", "-o", str(out)])

    assert result.exit_code == 0
    assert out.read_text() != "replace me"


@pytest.fixture
def terminal(monkeypatch) -> None:
    monkeypatch.setattr(cli, "is_interactive", lambda: True)


@pytest.mark.usefixtures("terminal")
def test_interactive_flow(monkeypatch, tmp_path) -> None:
    out = tmp_path / "LICENSE"
    asked: dict[str, str] = {}

    def ask_author(default: str) -> str:
        asked["author"] = default
        return "Ada Lovelace"

    def ask_year(default: str) -> str:
        asked["year"] = default
        return "1843"

    monkeypatch.setattr(prompts, "select_license", lambda _licenses: find("BSD-3-Clause"))
    monkeypatch.setattr(prompts, "ask_author", ask_author)
    monkeypatch.setattr(prompts, "ask_year", ask_year)

    result = runner.invoke(cli.app, ["license", "-o", str(out)])

    assert result.exit_code == 0
    assert asked["author"] == "Git User"
    assert asked["year"].isdigit()
    assert "Copyright (c) 1843, Ada Lovelace" in out.read_text()


@pytest.mark.usefixtures("terminal")
def test_interactive_skips_prompts_for_given_flags(monkeypatch, tmp_path) -> None:
    out = tmp_path / "LICENSE"

    def fail(*_args) -> str:
        raise AssertionError

    monkeypatch.setattr(prompts, "ask_author", fail)
    monkeypatch.setattr(prompts, "ask_year", fail)

    result = runner.invoke(cli.app, ["license", "mit", "-a", "Ada", "-y", "1843", "-o", str(out)])

    assert result.exit_code == 0


@pytest.mark.usefixtures("terminal")
@pytest.mark.parametrize(("answer", "replaced"), [(True, True), (False, False)])
def test_interactive_overwrite_confirmation(monkeypatch, tmp_path, answer, replaced) -> None:
    out = tmp_path / "LICENSE"
    out.write_text("old")
    monkeypatch.setattr(prompts, "confirm_overwrite", lambda _path: answer)

    result = runner.invoke(cli.app, ["license", "mit", "-a", "Ada", "-y", "1843", "-o", str(out)])

    assert (out.read_text() != "old") is replaced
    assert result.exit_code == (0 if replaced else 1)


@pytest.mark.usefixtures("terminal")
def test_no_command_runs_every_select_in_turn(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(prompts, "select_license", lambda _licenses: find("ISC"))
    monkeypatch.setattr(prompts, "ask_author", lambda _default: "Ada Lovelace")
    monkeypatch.setattr(prompts, "ask_year", lambda _default: "1843")
    monkeypatch.setattr(prompts, "select_templates", lambda _templates: [gitignore.find("Python")])

    result = runner.invoke(cli.app, [])

    assert result.exit_code == 0
    assert "Copyright (c) 1843 Ada Lovelace" in (tmp_path / "LICENSE").read_text()
    assert "### Python ###" in (tmp_path / ".gitignore").read_text()


@pytest.mark.usefixtures("terminal")
def test_no_command_stops_when_a_select_is_aborted(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)

    def abort(_licenses) -> None:
        raise typer.Abort

    monkeypatch.setattr(prompts, "select_license", abort)
    monkeypatch.setattr(prompts, "select_templates", lambda _templates: pytest.fail("should not be reached"))

    result = runner.invoke(cli.app, [])

    assert result.exit_code != 0
    assert not (tmp_path / ".gitignore").exists()
