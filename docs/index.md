# hinagata

A lightweight license generator CLI. Pick a license from a filterable list,
confirm the author and year, and get a `LICENSE` file.

## Installation

Try it without installing:

```sh
uvx hinagata
pipx run hinagata
```

Or install it:

```sh
uv tool install hinagata
pipx install hinagata
pip install hinagata
```

## Usage

Run `hinagata` to choose a license interactively, or pass everything as flags:

```sh
hinagata MIT --author "Ada Lovelace" --year 2026
hinagata Apache-2.0 --output LICENSE.txt --force
hinagata ISC -o - > LICENSE
hinagata --list
```

| Option         | Description                                               |
| -------------- | --------------------------------------------------------- |
| `[LICENSE]`    | SPDX identifier, case-insensitive. Asked when omitted.    |
| `-a, --author` | Copyright holder. Defaults to `git config user.name`.     |
| `-y, --year`   | Year or range such as `2020-2026`. Defaults to this year. |
| `-o, --output` | File to write, or `-` for stdout. Defaults to `LICENSE`.  |
| `-f, --force`  | Overwrite an existing file without asking.                |
| `-l, --list`   | List the available licenses.                              |

## Short alias

Every install also provides `hina`, which behaves exactly like `hinagata`:

```sh
hina MIT -a "Ada Lovelace"
```

Without installing, use `uvx --from hinagata hina`, since `uvx hina` would fetch
an unrelated package.

## Development

Install the project with `uv sync`, then run the test suite with
`uv run pytest`.
