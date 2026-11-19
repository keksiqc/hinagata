"""Generation of ``.editorconfig`` files."""

from __future__ import annotations

from enum import StrEnum


DEFAULT_SIZE = 4
MIN_SIZE = 1
MAX_SIZE = 16
COMPACT_SIZE = 2
COMPACT_GLOB = "*.{html,css,js,json,sh,yml,yaml,toml}"


class IndentStyle(StrEnum):
    """How a level of indentation is written."""

    SPACE = "space"
    TAB = "tab"


def is_valid_size(value: str) -> bool:
    """Whether the value is a whole number of columns, such as ``4``."""
    text = value.strip()
    return text.isascii() and text.isdigit() and MIN_SIZE <= int(text) <= MAX_SIZE


def render(style: IndentStyle = IndentStyle.SPACE, size: int = DEFAULT_SIZE) -> str:
    """Build an ``.editorconfig`` with the given indentation.

    Spaces get a compact override for web and config files, because those
    formats are conventionally indented by two. Tabs do not need it, since the
    reader chooses the width. Makefiles always need tabs, and Markdown needs
    its trailing double space, which marks a line break.
    """
    lines = [
        "# EditorConfig is awesome: https://editorconfig.org",
        "",
        "# top-most EditorConfig file",
        "root = true",
        "",
        "[*]",
        "charset = utf-8",
        "end_of_line = lf",
        f"indent_style = {style}",
        f"indent_size = {size}",
        "trim_trailing_whitespace = true",
        "insert_final_newline = true",
    ]
    if style is IndentStyle.SPACE and size != COMPACT_SIZE:
        lines += ["", f"[{COMPACT_GLOB}]", f"indent_size = {COMPACT_SIZE}"]
    if style is IndentStyle.SPACE:
        lines += ["", "[Makefile]", "indent_style = tab"]
    lines += ["", "[*.md]", "trim_trailing_whitespace = false"]
    return "\n".join(lines) + "\n"
