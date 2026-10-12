from __future__ import annotations

import pytest

from licensd.licenses import LICENSES, find


@pytest.mark.parametrize("lic", LICENSES, ids=lambda lic: lic.spdx_id)
def test_text_is_bundled(lic) -> None:
    assert lic.text.strip()


def test_ids_are_unique() -> None:
    ids = [lic.spdx_id.casefold() for lic in LICENSES]

    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("key", ["MIT", "mit", " Mit "])
def test_find_ignores_case(key) -> None:
    lic = find(key)

    assert lic is not None
    assert lic.spdx_id == "MIT"


def test_find_unknown() -> None:
    assert find("nope") is None


def test_render_fills_holder_and_year() -> None:
    lic = find("MIT")
    assert lic is not None

    text = lic.render("Ada Lovelace", "1843")

    assert "Copyright (c) 1843 Ada Lovelace" in text
    assert "[year]" not in text
    assert "[fullname]" not in text


@pytest.mark.parametrize(
    ("spdx_id", "expected"),
    [("MIT", True), ("BSD-3-Clause", True), ("ISC", True), ("GPL-3.0", False), ("Apache-2.0", False)],
)
def test_has_holder(spdx_id, expected) -> None:
    lic = find(spdx_id)
    assert lic is not None

    assert lic.has_holder is expected
