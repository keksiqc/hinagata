from __future__ import annotations

import pytest
from typer.testing import CliRunner

from hinagata import cli, gitignore, prompts
from hinagata.detect import MARKERS, detect


runner = CliRunner()


def _names(root) -> list[str]:
    return [template.name for template in detect(root)]


def test_every_marker_names_a_bundled_template() -> None:
    assert all(gitignore.find(name) is not None for name in MARKERS)


def test_empty_folder_detects_nothing(tmp_path) -> None:
    assert detect(tmp_path) == []


def test_missing_folder_detects_nothing(tmp_path) -> None:
    assert detect(tmp_path / "missing") == []


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("pyproject.toml", "Python"),
        ("requirements-dev.txt", "Python"),
        ("package.json", "Node"),
        ("Cargo.toml", "Rust"),
        ("go.mod", "Go"),
        ("App.csproj", "Dotnet"),
        ("main.tf", "Terraform"),
        ("mise.toml", "mise"),
        (".vscode", "VisualStudioCode"),
        (".idea", "JetBrains"),
    ],
)
def test_marker_is_detected(tmp_path, filename, expected) -> None:
    (tmp_path / filename).touch()

    assert expected in _names(tmp_path)


def test_results_follow_catalogue_order(tmp_path) -> None:
    for filename in ("package.json", "Cargo.toml", "pyproject.toml"):
        (tmp_path / filename).touch()

    assert _names(tmp_path) == ["Node", "Python", "Rust"]


def test_matches_are_case_sensitive(tmp_path) -> None:
    (tmp_path / "CARGO.TOML").touch()

    assert "Rust" not in _names(tmp_path)


def test_direct_subfolders_are_scanned(tmp_path) -> None:
    (tmp_path / "frontend").mkdir()
    (tmp_path / "frontend" / "package.json").touch()

    assert _names(tmp_path) == ["Node"]


def test_deeper_folders_are_not_scanned(tmp_path) -> None:
    (tmp_path / "a" / "b").mkdir(parents=True)
    (tmp_path / "a" / "b" / "package.json").touch()

    assert detect(tmp_path) == []


@pytest.mark.parametrize("folder", ["node_modules", "vendor", ".hidden"])
def test_third_party_and_hidden_folders_are_skipped(tmp_path, folder) -> None:
    (tmp_path / folder).mkdir()
    (tmp_path / folder / "package.json").touch()

    assert detect(tmp_path) == []


def test_cli_detects_next_to_the_output_file(tmp_path) -> None:
    (tmp_path / "Cargo.toml").touch()
    out = tmp_path / ".gitignore"

    result = runner.invoke(cli.app, ["gitignore", "--detect", "-o", str(out)])

    assert result.exit_code == 0
    assert out.read_text() == gitignore.render([_template("Rust")])


def test_cli_combines_names_with_detected(tmp_path) -> None:
    (tmp_path / "Cargo.toml").touch()
    out = tmp_path / ".gitignore"

    result = runner.invoke(cli.app, ["gitignore", "Linux", "-d", "-o", str(out)])

    assert result.exit_code == 0
    assert out.read_text() == gitignore.render([_template("Linux"), _template("Rust")])


def test_cli_does_not_repeat_a_named_template(tmp_path) -> None:
    (tmp_path / "Cargo.toml").touch()
    out = tmp_path / ".gitignore"

    result = runner.invoke(cli.app, ["gitignore", "rust", "-d", "-o", str(out)])

    assert result.exit_code == 0
    assert out.read_text().count("### Rust ###") == 1


def test_cli_fails_when_nothing_is_detected_without_terminal(tmp_path) -> None:
    out = tmp_path / ".gitignore"

    result = runner.invoke(cli.app, ["gitignore", "--detect", "-o", str(out)])

    assert result.exit_code == 2
    assert "nothing detected" in result.output
    assert not out.exists()


def test_cli_names_still_work_when_nothing_is_detected(tmp_path) -> None:
    out = tmp_path / ".gitignore"

    result = runner.invoke(cli.app, ["gitignore", "Linux", "-d", "-o", str(out)])

    assert result.exit_code == 0
    assert out.read_text() == gitignore.render([_template("Linux")])


def test_cli_works_with_append(tmp_path) -> None:
    (tmp_path / "Cargo.toml").touch()
    out = tmp_path / ".gitignore"
    out.write_text("secrets.txt\n")

    result = runner.invoke(cli.app, ["gitignore", "-d", "--append", "-o", str(out)])

    assert result.exit_code == 0
    assert out.read_text().startswith("secrets.txt\n\n### Rust ###")


@pytest.fixture
def terminal(monkeypatch) -> None:
    monkeypatch.setattr(cli, "is_interactive", lambda: True)


@pytest.mark.usefixtures("terminal")
def test_interactive_picker_starts_with_detected_templates(monkeypatch, tmp_path) -> None:
    (tmp_path / "Cargo.toml").touch()
    out = tmp_path / ".gitignore"
    seen: list[list[str]] = []

    def pick(_templates, selected=()):
        seen.append([template.name for template in selected])
        return list(selected)

    monkeypatch.setattr(prompts, "select_templates", pick)

    result = runner.invoke(cli.app, ["gitignore", "--detect", "-o", str(out)])

    assert result.exit_code == 0
    assert seen == [["Rust"]]
    assert out.read_text() == gitignore.render([_template("Rust")])


@pytest.mark.usefixtures("terminal")
def test_interactive_picker_still_opens_when_nothing_is_detected(monkeypatch, tmp_path) -> None:
    out = tmp_path / ".gitignore"
    monkeypatch.setattr(prompts, "select_templates", lambda _templates, selected=(): [_template("Linux")])

    result = runner.invoke(cli.app, ["gitignore", "--detect", "-o", str(out)])

    assert result.exit_code == 0
    assert out.read_text() == gitignore.render([_template("Linux")])


@pytest.mark.usefixtures("terminal")
def test_interactive_picker_is_skipped_when_names_are_given(monkeypatch, tmp_path) -> None:
    (tmp_path / "Cargo.toml").touch()
    out = tmp_path / ".gitignore"
    monkeypatch.setattr(prompts, "select_templates", lambda *_args, **_kwargs: pytest.fail("should not be reached"))

    result = runner.invoke(cli.app, ["gitignore", "Linux", "-d", "-o", str(out)])

    assert result.exit_code == 0
    assert out.read_text() == gitignore.render([_template("Linux"), _template("Rust")])


def _template(name: str) -> gitignore.Template:
    template = gitignore.find(name)
    assert template is not None
    return template
