# hinagata

A lightweight CLI to generate project files like `LICENSE` and `.gitignore`.
Pick from a filterable list, confirm the details, and get the file.

Also available as the shorter `hina`.

## Quick start

```sh
uvx hinagata
```

That runs `hinagata` once without installing anything. It walks you through
choosing a license, then gitignore templates. To keep it around:

```sh
uv tool install hinagata
hinagata
```

## Installation

| Method     | Run once              | Install                     | Upgrade                     |
| ---------- | --------------------- | --------------------------- | --------------------------- |
| `uv`       | `uvx hinagata`        | `uv tool install hinagata`  | `uv tool upgrade hinagata`  |
| `pipx`     | `pipx run hinagata`   | `pipx install hinagata`     | `pipx upgrade hinagata`     |
| `pip`      |                       | `pip install hinagata`      | `pip install -U hinagata`   |

`pip` installs into the current environment, so use a virtual environment or
`pip install --user hinagata`. With `uv`, `uv pip install hinagata` works the
same way.

To use the development version, install from Git or from a clone:

```sh
uv tool install git+https://github.com/keksiqc/hinagata
uv sync && uv run hinagata
```

`python -m hinagata` also works wherever the package is installed.

## Usage

Running `hinagata` with no command in a terminal goes through every select one
after another: the license (plus author and year where the license needs them),
then the gitignore templates. Without a terminal it prints the help instead.

The two steps are also available as separate commands, `license` and
`gitignore`. Run either without arguments to choose interactively. Everything
can also be passed as arguments and flags, which skips the matching prompt and
makes the command scriptable.

### License

```sh
hinagata license MIT --author "Ada Lovelace" --year 2026   # write ./LICENSE
hinagata license Apache-2.0 --output LICENSE.txt --force   # custom file, overwrite
hinagata license ISC -o - > LICENSE                        # print to stdout
hinagata license --list                                    # show the catalogue
```

| Option         | Description                                               |
| -------------- | --------------------------------------------------------- |
| `[LICENSE]`    | SPDX identifier, case-insensitive. Asked when omitted.    |
| `-a, --author` | Copyright holder. Defaults to `git config user.name`.     |
| `-y, --year`   | Year or range such as `2020-2026`. Defaults to this year. |
| `-o, --output` | File to write, or `-` for stdout. Defaults to `LICENSE`.  |
| `-f, --force`  | Overwrite an existing file without asking.                |
| `-l, --list`   | List the available licenses.                              |

Author and year are only asked for licenses whose text contains them (MIT, ISC,
BSD, 0BSD). The others, such as the GPL family and Apache-2.0, are written
verbatim.

### Gitignore

```sh
hinagata gitignore Python Linux VisualStudioCode   # write ./.gitignore
hinagata gitignore Node --append                   # add to an existing file
hinagata gitignore Rust -o - > .gitignore          # print to stdout
hinagata gitignore --list                          # show the templates
```

Each template is written under a `### Name ###` header, so you can see where a
block came from. Without arguments you get a checklist where you can type to
filter and pick as many templates as you need.

| Option         | Description                                                           |
| -------------- | --------------------------------------------------------------------- |
| `[TEMPLATE]...`| Template names, case-insensitive. Asked when omitted.                 |
| `-o, --output` | File to write, or `-` for stdout. Defaults to `.gitignore`.           |
| `-f, --force`  | Replace an existing file without asking.                              |
| `--append`     | Add the templates the file is missing, leaving everything else alone. |
| `-l, --list`   | List the available templates.                                         |

If the file already exists, a terminal session asks whether to append,
overwrite or cancel. Without a terminal the command fails unless you pass
`--force` or `--append`. Appending is safe to repeat: templates whose header is
already in the file are skipped.

### Short alias

`hina` is an alias for `hinagata` and takes the same arguments, which is handy
for everyday use once it is installed:

```sh
hina license MIT -a "Ada Lovelace"
hina gitignore Python
```

It ships inside the `hinagata` package rather than as a package of its own, so
`uvx hina` would fetch an unrelated project from PyPI. To run the alias without
installing, name the package explicitly:

```sh
uvx --from hinagata hina license MIT
pipx run --spec hinagata hina license MIT
```

## Bundled licenses

MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, 0BSD, BSL-1.0, MPL-2.0,
LGPL-3.0, GPL-2.0, GPL-3.0, AGPL-3.0, Unlicense and CC0-1.0. The texts come
from [choosealicense.com](https://github.com/github/choosealicense.com).

## Bundled gitignore templates

About 240 templates from [github/gitignore](https://github.com/github/gitignore)
(CC0): the language and tool templates such as Python, Node and Rust, plus the
`Global` ones for editors and operating systems such as VisualStudioCode, Linux
and macOS. Refresh them with `python scripts/update_gitignore.py`, which also
records the upstream commit in `src/hinagata/data/gitignore/SOURCE`.

## Development

Install the project and its development dependencies:

```sh
uv sync
```

Run the checks:

```sh
uv run ruff format --check .
uv run ruff check .
uv run ty check .
uv run pytest
```
