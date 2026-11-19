"""Guess gitignore templates from the files in a project folder."""

from __future__ import annotations

from fnmatch import fnmatchcase
from typing import TYPE_CHECKING

from .gitignore import catalogue


if TYPE_CHECKING:
    from pathlib import Path

    from .gitignore import Template


# Template name -> file or folder names (``fnmatch`` patterns) that give the project away.
MARKERS: dict[str, tuple[str, ...]] = {
    # Languages and package managers
    "Python": ("pyproject.toml", "setup.py", "setup.cfg", "requirements*.txt", "Pipfile", "uv.lock"),
    "Node": ("package.json",),
    "bun": ("bun.lock", "bun.lockb"),
    "Deno": ("deno.json", "deno.jsonc"),
    "Rust": ("Cargo.toml",),
    "Go": ("go.mod",),
    "Java": ("pom.xml", "build.gradle", "build.gradle.kts"),
    "Maven": ("pom.xml",),
    "Gradle": ("build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"),
    "Scala": ("build.sbt",),
    "SBT": ("build.sbt",),
    "Ruby": ("Gemfile", "*.gemspec"),
    "Composer": ("composer.json",),
    "Laravel": ("artisan",),
    "Dotnet": ("*.csproj", "*.fsproj", "*.vbproj", "*.sln", "*.slnx"),
    "Swift": ("Package.swift",),
    "Dart": ("pubspec.yaml",),
    "Elixir": ("mix.exs",),
    "Gleam": ("gleam.toml",),
    "Haskell": ("*.cabal", "stack.yaml"),
    "Julia": ("Project.toml",),
    "Leiningen": ("project.clj",),
    "Zig": ("build.zig",),
    "Lua": ("*.rockspec",),
    "CMake": ("CMakeLists.txt",),
    "TeX": ("*.tex",),
    # Frameworks and engines
    "Nextjs": ("next.config.js", "next.config.mjs", "next.config.ts"),
    "Nestjs": ("nest-cli.json",),
    "Angular": ("angular.json",),
    "Godot": ("project.godot",),
    "Unity": ("ProjectSettings",),
    # Infrastructure and tooling
    "Terraform": ("*.tf",),
    "Packer": ("*.pkr.hcl",),
    "Nix": ("flake.nix",),
    "mise": ("mise.toml", ".mise.toml"),
    # Editors
    "VisualStudioCode": (".vscode",),
    "JetBrains": (".idea",),
    "Zed": (".zed",),
}

# Folders that hold third-party or generated files, so their contents say nothing about the project.
SKIPPED_FOLDERS = frozenset({"node_modules", "vendor", "target", "venv", "dist", "build", "site-packages"})


def detect(root: Path) -> list[Template]:
    """Templates that match the files in ``root`` and in its direct subfolders.

    Subfolders are included so that a monorepo with ``frontend/package.json``
    is noticed. Hidden folders and folders of third-party code are not entered.
    """
    names = _names(root)
    return [
        template
        for template in catalogue()
        if any(fnmatchcase(name, pattern) for pattern in MARKERS.get(template.name, ()) for name in names)
    ]


def _names(root: Path) -> set[str]:
    names: set[str] = set()
    try:
        entries = list(root.iterdir())
    except OSError:
        return names
    for entry in entries:
        names.add(entry.name)
        if _is_scannable(entry):
            try:
                names.update(child.name for child in entry.iterdir())
            except OSError:
                continue
    return names


def _is_scannable(entry: Path) -> bool:
    try:
        is_folder = entry.is_dir()
    except OSError:
        return False
    return is_folder and not entry.name.startswith(".") and entry.name not in SKIPPED_FOLDERS
