"""Catalogue of bundled licenses and their rendering."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cache
from importlib.resources import files


YEAR_PLACEHOLDER = "[year]"
AUTHOR_PLACEHOLDER = "[fullname]"
_YEAR_PATTERN = re.compile(r"\d{4}(-\d{4})?")


@dataclass(frozen=True, slots=True)
class License:
    """A license template bundled with the package."""

    spdx_id: str
    name: str
    summary: str

    @property
    def text(self) -> str:
        """Raw license text, placeholders included."""
        return _read(f"{self.spdx_id.lower()}.txt")

    @property
    def has_holder(self) -> bool:
        """Whether the license names a copyright holder and year."""
        return YEAR_PLACEHOLDER in self.text

    def render(self, author: str, year: str) -> str:
        """Fill in the copyright holder and year."""
        return self.text.replace(YEAR_PLACEHOLDER, year).replace(AUTHOR_PLACEHOLDER, author)


@cache
def _read(filename: str) -> str:
    return files("licensd").joinpath("data", filename).read_text(encoding="utf-8")


LICENSES: tuple[License, ...] = (
    License("MIT", "MIT License", "Short and permissive, only requires keeping the notice"),
    License("Apache-2.0", "Apache License 2.0", "Permissive, with an explicit patent grant"),
    License("BSD-2-Clause", 'BSD 2-Clause "Simplified"', "Permissive, minimal conditions"),
    License(
        "BSD-3-Clause", 'BSD 3-Clause "New" or "Revised"', "Permissive, forbids using the author's name to endorse"
    ),
    License("ISC", "ISC License", "Functionally equivalent to MIT, with simpler wording"),
    License("0BSD", "BSD Zero Clause", "Public-domain-like, no attribution required"),
    License("BSL-1.0", "Boost Software License 1.0", "Permissive, no notice needed in binaries"),
    License("MPL-2.0", "Mozilla Public License 2.0", "Weak copyleft, applies per file"),
    License("LGPL-3.0", "GNU LGPL v3.0", "Weak copyleft, safe to link from proprietary code"),
    License("GPL-2.0", "GNU GPL v2.0", "Strong copyleft, derivative works stay open"),
    License("GPL-3.0", "GNU GPL v3.0", "Strong copyleft with patent and anti-tivoization terms"),
    License("AGPL-3.0", "GNU AGPL v3.0", "Strong copyleft that also covers network use"),
    License("Unlicense", "The Unlicense", "Dedicates the work to the public domain"),
    License("CC0-1.0", "Creative Commons Zero v1.0", "Public domain dedication with a fallback license"),
)


def find(key: str) -> License | None:
    """Look a license up by SPDX identifier, ignoring case."""
    wanted = key.strip().casefold()
    return next((lic for lic in LICENSES if lic.spdx_id.casefold() == wanted), None)


def is_valid_year(value: str) -> bool:
    """Whether the value is a year such as ``2026`` or a range such as ``2020-2026``."""
    return _YEAR_PATTERN.fullmatch(value.strip()) is not None
