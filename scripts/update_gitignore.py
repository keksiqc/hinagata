"""Refresh the bundled gitignore templates from github/gitignore.

Usage: python scripts/update_gitignore.py [CHECKOUT]

Without an argument the upstream repository is cloned into a temporary directory.
"""

from __future__ import annotations

import shutil
import subprocess  # noqa: S404
import sys
import tempfile
from pathlib import Path


UPSTREAM = "https://github.com/github/gitignore.git"
TARGET = Path(__file__).resolve().parent.parent / "src" / "hinagata" / "data" / "gitignore"


def git(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, check=True, text=True)  # noqa: S603, S607
    return result.stdout.strip()


def copy_templates(source: Path) -> int:
    if TARGET.exists():
        shutil.rmtree(TARGET)
    TARGET.mkdir(parents=True)
    count = 0
    for folder, destination in ((source, TARGET), (source / "Global", TARGET / "Global")):
        destination.mkdir(exist_ok=True)
        for template in sorted(folder.glob("*.gitignore")):
            shutil.copyfile(template, destination / template.name)
            count += 1
    return count


def main() -> None:
    if len(sys.argv) > 1:
        source = Path(sys.argv[1])
        count = copy_templates(source)
        revision = git("rev-parse", "HEAD", cwd=source)
    else:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "gitignore"
            git("clone", "--depth", "1", UPSTREAM, str(source))
            count = copy_templates(source)
            revision = git("rev-parse", "HEAD", cwd=source)
    (TARGET / "SOURCE").write_text(
        f"{UPSTREAM.removesuffix('.git')}\ncommit {revision}\nlicense CC0-1.0\n", encoding="utf-8"
    )
    print(f"Copied {count} templates from {revision[:12]}")


if __name__ == "__main__":
    main()
