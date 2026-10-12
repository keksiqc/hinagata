"""Command-line interface for the package."""

from __future__ import annotations

import argparse
from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> None:
    """Run the command-line interface."""
    parser = argparse.ArgumentParser(
        prog="template-pypackage",
        description="A Python package.",
    )
    parser.add_argument(
        "name",
        nargs="?",
        default="template-pypackage",
        help="Name to include in the greeting.",
    )
    args = parser.parse_args(argv)
    print(f"Hello from {args.name}!")
