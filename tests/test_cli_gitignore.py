from __future__ import annotations

import pytest
from typer.testing import CliRunner

from hinagata import cli, gitignore, prompts


runner = CliRunner()


def _template(name: str) -> gitignore.Template:
    template = gitignore.find(name)
    assert template is not None
    return template


def test_list_shows_templates() -> None:
    result = runner.invoke(cli.app, ["gitignore", "--list"])

    assert result.exit_code == 0
    assert "Python" in result.stdout
    assert "VisualStudioCode" in result.stdout


def test_writes_combined_file(tmp_path) -> None:
    out = tmp_path / ".gitignore"

    result = runner.invoke(cli.app, ["gitignore", "python", "Linux", "-o", str(out)])

    assert result.exit_code == 0
    assert out.read_text() == gitignore.render([_template("Python"), _template("Linux")])


def test_duplicate_names_are_collapsed(tmp_path) -> None:
    out = tmp_path / ".gitignore"

    result = runner.invoke(cli.app, ["gitignore", "Python", "python", "-o", str(out)])

    assert result.exit_code == 0
    assert out.read_text().count("### Python ###") == 1


def test_stdout_output() -> None:
    result = runner.invoke(cli.app, ["gitignore", "Node", "-o", "-"])

    assert result.exit_code == 0
    assert result.stdout.startswith("### Node ###")


def test_unknown_template_suggests_match() -> None:
    result = runner.invoke(cli.app, ["gitignore", "Pythn"])

    assert result.exit_code == 2
    assert "Did you mean Python?" in result.output


def test_missing_template_without_terminal() -> None:
    result = runner.invoke(cli.app, ["gitignore"])

    assert result.exit_code == 2


def test_refuses_to_overwrite(tmp_path) -> None:
    out = tmp_path / ".gitignore"
    out.write_text("keep me")

    result = runner.invoke(cli.app, ["gitignore", "Python", "-o", str(out)])

    assert result.exit_code == 1
    assert out.read_text() == "keep me"


def test_force_overwrites(tmp_path) -> None:
    out = tmp_path / ".gitignore"
    out.write_text("replace me")

    result = runner.invoke(cli.app, ["gitignore", "Python", "-f", "-o", str(out)])

    assert result.exit_code == 0
    assert "replace me" not in out.read_text()


def test_append_adds_missing_templates(tmp_path) -> None:
    out = tmp_path / ".gitignore"
    out.write_text("secrets.txt\n")

    result = runner.invoke(cli.app, ["gitignore", "Python", "--append", "-o", str(out)])

    assert result.exit_code == 0
    assert out.read_text().startswith("secrets.txt\n\n### Python ###")


def test_append_is_idempotent(tmp_path) -> None:
    out = tmp_path / ".gitignore"
    args = ["gitignore", "Python", "--append", "-o", str(out)]
    runner.invoke(cli.app, args)
    first = out.read_text()

    result = runner.invoke(cli.app, args)

    assert result.exit_code == 0
    assert out.read_text() == first


def test_append_creates_missing_file(tmp_path) -> None:
    out = tmp_path / ".gitignore"

    result = runner.invoke(cli.app, ["gitignore", "Python", "--append", "-o", str(out)])

    assert result.exit_code == 0
    assert out.read_text() == gitignore.render([_template("Python")])


def test_append_and_force_conflict(tmp_path) -> None:
    result = runner.invoke(cli.app, ["gitignore", "Python", "--append", "-f", "-o", str(tmp_path / ".gitignore")])

    assert result.exit_code == 2


@pytest.fixture
def terminal(monkeypatch) -> None:
    monkeypatch.setattr(cli, "is_interactive", lambda: True)


@pytest.mark.usefixtures("terminal")
def test_interactive_selection(monkeypatch, tmp_path) -> None:
    out = tmp_path / ".gitignore"
    monkeypatch.setattr(prompts, "select_templates", lambda _templates: [_template("Rust"), _template("macOS")])

    result = runner.invoke(cli.app, ["gitignore", "-o", str(out)])

    assert result.exit_code == 0
    assert out.read_text() == gitignore.render([_template("Rust"), _template("macOS")])


@pytest.mark.usefixtures("terminal")
@pytest.mark.parametrize(
    ("choice", "expected_header_count", "kept"),
    [("append", 1, True), ("overwrite", 1, False)],
)
def test_interactive_existing_file(monkeypatch, tmp_path, choice, expected_header_count, kept) -> None:
    out = tmp_path / ".gitignore"
    out.write_text("secrets.txt\n")
    monkeypatch.setattr(prompts, "ask_existing", lambda _path: choice)

    result = runner.invoke(cli.app, ["gitignore", "Python", "-o", str(out)])

    assert result.exit_code == 0
    assert out.read_text().count("### Python ###") == expected_header_count
    assert ("secrets.txt" in out.read_text()) is kept


@pytest.mark.usefixtures("terminal")
def test_interactive_cancel_keeps_file(monkeypatch, tmp_path) -> None:
    out = tmp_path / ".gitignore"
    out.write_text("keep me")
    monkeypatch.setattr(prompts, "ask_existing", lambda _path: "cancel")

    result = runner.invoke(cli.app, ["gitignore", "Python", "-o", str(out)])

    assert result.exit_code != 0
    assert out.read_text() == "keep me"
