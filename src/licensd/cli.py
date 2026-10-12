"""Command-line interface for licensd."""

from __future__ import annotations

import difflib
import getpass
import subprocess  # noqa: S404
import sys
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from . import prompts
from .licenses import LICENSES, License, find, is_valid_year


STDOUT = "-"

app = typer.Typer(add_completion=False, help="Generate a license file for your project.")
console = Console(stderr=True)


@app.command()
def generate(
    license_id: Annotated[
        str | None,
        typer.Argument(metavar="[LICENSE]", help="SPDX identifier such as MIT. Asked interactively when omitted."),
    ] = None,
    author: Annotated[str | None, typer.Option("--author", "-a", help="Copyright holder.")] = None,
    year: Annotated[str | None, typer.Option("--year", "-y", help="Copyright year or range.")] = None,
    output: Annotated[Path, typer.Option("--output", "-o", help="File to write, or - for stdout.")] = Path("LICENSE"),
    force: Annotated[bool, typer.Option("--force", "-f", help="Overwrite an existing file.")] = False,
    list_licenses: Annotated[bool, typer.Option("--list", "-l", help="List the available licenses.")] = False,
    show_version: Annotated[bool, typer.Option("--version", help="Show the version.", is_eager=True)] = False,
) -> None:
    """Generate a license file for your project."""
    if show_version:
        typer.echo(version("licensd"))
        raise typer.Exit
    if list_licenses:
        _print_catalogue()
        raise typer.Exit
    if year is not None and not is_valid_year(year):
        msg = "use a year like 2026 or a range like 2020-2026"
        raise typer.BadParameter(msg, param_hint="--year")

    interactive = is_interactive()
    lic = _resolve_license(license_id, interactive=interactive)
    holder, years = _resolve_holder(lic, author, year, interactive=interactive)
    text = lic.render(holder, years)

    if str(output) == STDOUT:
        typer.echo(text, nl=False)
        return
    _check_overwrite(output, force=force, interactive=interactive)
    output.write_text(text, encoding="utf-8")
    console.print(f"[green]✓[/] Wrote [bold]{lic.name}[/] to [cyan]{output}[/]")


def is_interactive() -> bool:
    """Whether prompts can be shown."""
    return sys.stdin.isatty() and sys.stdout.isatty()


def default_author() -> str:
    """Best guess at the copyright holder: the git user, else the login name."""
    try:
        result = subprocess.run(
            ["git", "config", "user.name"],  # noqa: S607
            capture_output=True,
            check=False,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return getpass.getuser()
    return result.stdout.strip() or getpass.getuser()


def _resolve_license(license_id: str | None, *, interactive: bool) -> License:
    if license_id is None:
        if not interactive:
            msg = "no license given; pass an SPDX identifier or run in a terminal (see --list)"
            raise typer.BadParameter(msg, param_hint="LICENSE")
        return prompts.select_license(LICENSES)
    lic = find(license_id)
    if lic is None:
        known = {known.spdx_id.casefold(): known.spdx_id for known in LICENSES}
        close = difflib.get_close_matches(license_id.casefold(), known, n=1, cutoff=0.5)
        hint = f" Did you mean {known[close[0]]}?" if close else " See --list."
        msg = f"unknown license {license_id!r}.{hint}"
        raise typer.BadParameter(msg, param_hint="LICENSE")
    return lic


def _resolve_holder(lic: License, author: str | None, year: str | None, *, interactive: bool) -> tuple[str, str]:
    if not lic.has_holder:
        return "", ""
    default_year = str(datetime.now(UTC).year)
    if interactive:
        author = author or prompts.ask_author(default_author())
        year = year or prompts.ask_year(default_year)
    return author or default_author(), year or default_year


def _check_overwrite(output: Path, *, force: bool, interactive: bool) -> None:
    if force or not output.exists():
        return
    if interactive and prompts.confirm_overwrite(output):
        return
    if interactive:
        raise typer.Abort
    console.print(f"[red]error:[/] {output} already exists, use --force to overwrite")
    raise typer.Exit(1)


def _print_catalogue() -> None:
    table = Table(box=None, pad_edge=False, header_style="bold")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Summary", style="dim")
    for lic in LICENSES:
        table.add_row(lic.spdx_id, lic.name, lic.summary)
    Console().print(table)
