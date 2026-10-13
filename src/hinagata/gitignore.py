"""Catalogue of bundled gitignore templates and their rendering."""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from importlib.resources import files
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Iterable
    from importlib.resources.abc import Traversable


SUFFIX = ".gitignore"
PROJECT = "Project"
GLOBAL = "Global"


@dataclass(frozen=True, slots=True)
class Template:
    """A gitignore template bundled with the package."""

    name: str
    group: str

    @property
    def text(self) -> str:
        """Raw template text."""
        folder = _root().joinpath(GLOBAL) if self.group == GLOBAL else _root()
        return folder.joinpath(f"{self.name}{SUFFIX}").read_text(encoding="utf-8")

    @property
    def header(self) -> str:
        """Marker line that introduces the template in a combined file."""
        return f"### {self.name} ###"


def _root() -> Traversable:
    return files("hinagata").joinpath("data", "gitignore")


def _scan(folder: Traversable, group: str) -> list[Template]:
    return [
        Template(entry.name.removesuffix(SUFFIX), group)
        for entry in folder.iterdir()
        if entry.is_file() and entry.name.endswith(SUFFIX)
    ]


@cache
def catalogue() -> tuple[Template, ...]:
    """Every bundled template, sorted by name."""
    root = _root()
    found = _scan(root, PROJECT) + _scan(root.joinpath(GLOBAL), GLOBAL)
    return tuple(sorted(found, key=lambda template: template.name.casefold()))


def find(key: str) -> Template | None:
    """Look a template up by name, ignoring case."""
    wanted = key.strip().casefold()
    return next((template for template in catalogue() if template.name.casefold() == wanted), None)


def render(templates: Iterable[Template]) -> str:
    """Join templates into one file, each under its own header."""
    return "\n".join(f"{template.header}\n{template.text.rstrip()}\n" for template in templates)


def merge(existing: str, templates: Iterable[Template]) -> str:
    """Add the templates that are not in ``existing`` yet, leaving the rest untouched."""
    present = {line.strip() for line in existing.splitlines()}
    missing = [template for template in templates if template.header not in present]
    if not missing:
        return existing
    block = render(missing)
    if not existing.strip():
        return block
    return f"{existing.rstrip()}\n\n{block}"
