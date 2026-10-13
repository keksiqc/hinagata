# hinagata

A lightweight license generator CLI. Pick a license from a filterable list,
confirm the author and year, and get a `LICENSE` file.

Also available as the shorter `hina`.

## Quick start

```sh
uvx hinagata
```

That runs `hinagata` once without installing anything. To keep it around:

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

Run without arguments to choose a license interactively. Everything can also be
passed as flags, which skips the matching prompt and makes the command
scriptable:

```sh
hinagata MIT --author "Ada Lovelace" --year 2026   # write ./LICENSE
hinagata Apache-2.0 --output LICENSE.txt --force   # custom file, overwrite
hinagata ISC -o - > LICENSE                        # print to stdout
hinagata --list                                    # show the catalogue
```

| Option         | Description                                               |
| -------------- | --------------------------------------------------------- |
| `[LICENSE]`    | SPDX identifier, case-insensitive. Asked when omitted.    |
| `-a, --author` | Copyright holder. Defaults to `git config user.name`.     |
| `-y, --year`   | Year or range such as `2020-2026`. Defaults to this year. |
| `-o, --output` | File to write, or `-` for stdout. Defaults to `LICENSE`.  |
| `-f, --force`  | Overwrite an existing file without asking.                |
| `-l, --list`   | List the available licenses.                              |
| `--version`    | Show the version.                                         |

Author and year are only asked for licenses whose text contains them (MIT, ISC,
BSD, 0BSD). The others, such as the GPL family and Apache-2.0, are written
verbatim.

### Short alias

`hina` is an alias for `hinagata` and takes the same arguments, which is handy
for everyday use once it is installed:

```sh
hina MIT -a "Ada Lovelace"
```

It ships inside the `hinagata` package rather than as a package of its own, so
`uvx hina` would fetch an unrelated project from PyPI. To run the alias without
installing, name the package explicitly:

```sh
uvx --from hinagata hina MIT
pipx run --spec hinagata hina MIT
```

## Bundled licenses

MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, 0BSD, BSL-1.0, MPL-2.0,
LGPL-3.0, GPL-2.0, GPL-3.0, AGPL-3.0, Unlicense and CC0-1.0. The texts come
from [choosealicense.com](https://github.com/github/choosealicense.com).

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
