"""Command-line interface for hinagata."""

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

from . import gitignore, prompts
from .licenses import LICENSES, License, find, is_valid_year


STDOUT = "-"

app = typer.Typer(add_completion=False, help="Generate project files such as a license and a gitignore.")
console = Console(stderr=True)


def _show_version(value: bool) -> None:
    if value:
        typer.echo(version("hinagata"))
        raise typer.Exit


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    _version: Annotated[
        bool, typer.Option("--version", help="Show the version.", callback=_show_version, is_eager=True)
    ] = False,
) -> None:
    """Generate project files such as a license and a gitignore.

    Run without a command to be guided through both, one after the other.
    """
    if ctx.invoked_subcommand is not None:
        return
    if not is_interactive():
        typer.echo(ctx.get_help())
        raise typer.Exit
    license_command()
    gitignore_command()


@app.command("license")
def license_command(
    license_id: Annotated[
        str | None,
        typer.Argument(metavar="[LICENSE]", help="SPDX identifier such as MIT. Asked interactively when omitted."),
    ] = None,
    author: Annotated[str | None, typer.Option("--author", "-a", help="Copyright holder.")] = None,
    year: Annotated[str | None, typer.Option("--year", "-y", help="Copyright year or range.")] = None,
    output: Annotated[Path, typer.Option("--output", "-o", help="File to write, or - for stdout.")] = Path("LICENSE"),
    force: Annotated[bool, typer.Option("--force", "-f", help="Overwrite an existing file.")] = False,
    list_licenses: Annotated[bool, typer.Option("--list", "-l", help="List the available licenses.")] = False,
) -> None:
    """Generate a license file for your project."""
    if list_licenses:
        _print_licenses()
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


@app.command("gitignore")
def gitignore_command(
    names: Annotated[
        list[str] | None,
        typer.Argument(
            metavar="[TEMPLATE]...", help="Template names such as Python. Asked interactively when omitted."
        ),
    ] = None,
    output: Annotated[Path, typer.Option("--output", "-o", help="File to write, or - for stdout.")] = Path(
        ".gitignore"
    ),
    force: Annotated[bool, typer.Option("--force", "-f", help="Overwrite an existing file.")] = False,
    append: Annotated[
        bool, typer.Option("--append", help="Add the templates missing from an existing file instead of replacing it.")
    ] = False,
    list_templates: Annotated[bool, typer.Option("--list", "-l", help="List the available templates.")] = False,
) -> None:
    """Generate a .gitignore file from one or more templates."""
    if list_templates:
        _print_templates()
        raise typer.Exit
    if append and force:
        msg = "--append and --force cannot be combined"
        raise typer.BadParameter(msg, param_hint="--append")

    interactive = is_interactive()
    templates = _resolve_templates(names, interactive=interactive)
    text = gitignore.render(templates)
    label = ", ".join(template.name for template in templates)

    if str(output) == STDOUT:
        typer.echo(text, nl=False)
        return
    if output.exists() and not force:
        append = append or _ask_existing(output, interactive=interactive)
    if append and output.exists():
        existing = output.read_text(encoding="utf-8")
        text = gitignore.merge(existing, templates)
        if text == existing:
            console.print(f"[yellow]![/] [cyan]{output}[/] already contains {label}")
            return
    output.write_text(text, encoding="utf-8")
    console.print(f"[green]✓[/] Wrote [bold]{label}[/] to [cyan]{output}[/]")


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
        msg = f"unknown license {license_id!r}.{_suggest(license_id, [known.spdx_id for known in LICENSES])}"
        raise typer.BadParameter(msg, param_hint="LICENSE")
    return lic


def _resolve_templates(names: list[str] | None, *, interactive: bool) -> list[gitignore.Template]:
    if not names:
        if not interactive:
            msg = "no template given; pass one or more names or run in a terminal (see --list)"
            raise typer.BadParameter(msg, param_hint="TEMPLATE")
        return prompts.select_templates(gitignore.catalogue())
    templates: dict[str, gitignore.Template] = {}
    for name in names:
        template = gitignore.find(name)
        if template is None:
            msg = f"unknown template {name!r}.{_suggest(name, [known.name for known in gitignore.catalogue()])}"
            raise typer.BadParameter(msg, param_hint="TEMPLATE")
        templates[template.name] = template
    return list(templates.values())


def _suggest(key: str, candidates: list[str]) -> str:
    known = {candidate.casefold(): candidate for candidate in candidates}
    close = difflib.get_close_matches(key.casefold(), known, n=1, cutoff=0.5)
    return f" Did you mean {known[close[0]]}?" if close else " See --list."


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


def _ask_existing(output: Path, *, interactive: bool) -> bool:
    """Decide what to do with an existing file; returns whether to append to it."""
    if not interactive:
        console.print(f"[red]error:[/] {output} already exists, use --force to overwrite or --append to add to it")
        raise typer.Exit(1)
    choice = prompts.ask_existing(output)
    if choice == "cancel":
        raise typer.Abort
    return choice == "append"


def _print_licenses() -> None:
    table = Table(box=None, pad_edge=False, header_style="bold")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Summary", style="dim")
    for lic in LICENSES:
        table.add_row(lic.spdx_id, lic.name, lic.summary)
    Console().print(table)


def _print_templates() -> None:
    table = Table(box=None, pad_edge=False, header_style="bold")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Group", style="dim")
    for template in gitignore.catalogue():
        table.add_row(template.name, template.group)
    Console().print(table)
