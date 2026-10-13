from __future__ import annotations

import pytest

from hinagata import gitignore
from hinagata.gitignore import GLOBAL, PROJECT


def _template(name: str) -> gitignore.Template:
    template = gitignore.find(name)
    assert template is not None
    return template


def test_catalogue_is_sorted_and_unique() -> None:
    names = [template.name.casefold() for template in gitignore.catalogue()]

    assert names == sorted(names)
    assert len(names) == len(set(names))


def test_catalogue_has_both_groups() -> None:
    groups = {template.group for template in gitignore.catalogue()}

    assert groups == {PROJECT, GLOBAL}
    assert _template("Python").group == PROJECT
    assert _template("Linux").group == GLOBAL


@pytest.mark.parametrize("template", gitignore.catalogue(), ids=lambda template: template.name)
def test_every_template_has_text(template: gitignore.Template) -> None:
    assert template.text.strip()


def test_find_ignores_case_and_whitespace() -> None:
    assert gitignore.find(" python ") == _template("Python")
    assert gitignore.find("macos") == _template("macOS")
    assert gitignore.find("nope") is None


def test_render_adds_headers_in_order() -> None:
    text = gitignore.render([_template("Python"), _template("Linux")])

    assert text.index("### Python ###") < text.index("### Linux ###")
    assert "__pycache__/" in text
    assert text.endswith("\n")
    assert "\n\n### Linux ###\n" in text


def test_merge_into_empty_file_equals_render() -> None:
    templates = [_template("Python")]

    assert gitignore.merge("", templates) == gitignore.render(templates)


def test_merge_keeps_existing_content() -> None:
    merged = gitignore.merge("secrets.txt\n", [_template("Python")])

    assert merged.startswith("secrets.txt\n\n### Python ###\n")


def test_merge_skips_templates_already_present() -> None:
    first = gitignore.merge("", [_template("Python")])
    second = gitignore.merge(first, [_template("Python"), _template("Linux")])

    assert second.count("### Python ###") == 1
    assert "### Linux ###" in second
    assert gitignore.merge(second, [_template("Python"), _template("Linux")]) == second
