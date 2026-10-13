"""Interactive prompts."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import questionary
import typer

from .gitignore import Template
from .licenses import License, is_valid_year


STYLE = questionary.Style(
    [
        ("qmark", "fg:ansicyan bold"),
        ("question", "bold"),
        ("pointer", "fg:ansicyan bold"),
        ("highlighted", "fg:ansicyan bold"),
        ("answer", "fg:ansicyan"),
        ("instruction", "fg:ansibrightblack"),
    ]
)
QMARK = "◆"


def select_license(licenses: Sequence[License]) -> License:
    """Let the user pick a license from a filterable list."""
    width = max(len(lic.spdx_id) for lic in licenses)
    choices = [questionary.Choice(f"{lic.spdx_id:<{width}}  {lic.summary}", value=lic) for lic in licenses]
    question = questionary.select(
        "Choose a license",
        choices=choices,
        qmark=QMARK,
        style=STYLE,
        pointer="\u276f",
        instruction="(type to filter)",
        use_search_filter=True,
        use_jk_keys=False,
    )
    return _ask(question)


def select_templates(templates: Sequence[Template]) -> list[Template]:
    """Let the user pick one or more gitignore templates from a filterable list."""
    width = max(len(template.name) for template in templates)
    choices = [
        questionary.Choice(f"{template.name:<{width}}  {template.group}", value=template) for template in templates
    ]
    question = questionary.checkbox(
        "Choose gitignore templates",
        choices=choices,
        qmark=QMARK,
        style=STYLE,
        pointer="\u276f",
        instruction="(type to filter, space to select)",
        validate=lambda picked: bool(picked) or "Select at least one template",
        use_search_filter=True,
        use_jk_keys=False,
    )
    return _ask(question)


def ask_author(default: str) -> str:
    """Ask for the copyright holder."""
    question = questionary.text(
        "Author",
        default=default,
        qmark=QMARK,
        style=STYLE,
        validate=lambda value: bool(value.strip()) or "Please enter a name",
    )
    return _ask(question).strip()


def ask_year(default: str) -> str:
    """Ask for the copyright year."""
    question = questionary.text(
        "Year",
        default=default,
        qmark=QMARK,
        style=STYLE,
        validate=lambda value: is_valid_year(value) or "Use a year like 2026 or a range like 2020-2026",
    )
    return _ask(question).strip()


def confirm_overwrite(path: Path) -> bool:
    """Ask whether an existing file may be replaced."""
    question = questionary.confirm(f"{path} already exists. Overwrite?", default=False, qmark=QMARK, style=STYLE)
    return _ask(question)


def ask_existing(path: Path) -> str:
    """Ask what to do with an existing file: ``append``, ``overwrite`` or ``cancel``."""
    question = questionary.select(
        f"{path} already exists",
        choices=[
            questionary.Choice("Append the missing templates", value="append"),
            questionary.Choice("Overwrite it", value="overwrite"),
            questionary.Choice("Cancel", value="cancel"),
        ],
        qmark=QMARK,
        style=STYLE,
        pointer="\u276f",
        use_jk_keys=False,
    )
    return _ask(question)


def _ask[T](question: questionary.Question) -> T:
    answer = question.ask()
    if answer is None:
        raise typer.Abort
    return answer
