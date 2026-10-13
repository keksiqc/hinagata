# hinagata

A lightweight CLI that generates the boilerplate files for a new project:
a `LICENSE` and a `.gitignore`. Pick from a filterable list, confirm the
details, and get the file.

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

Running `hinagata` with no command in a terminal goes through every select one
after another: the license, then the gitignore templates.

The two steps are also available as separate commands, `license` and
`gitignore`. Run either without arguments to choose interactively, or pass
everything as arguments and flags.

### License

```sh
hinagata license MIT --author "Ada Lovelace" --year 2026
hinagata license Apache-2.0 --output LICENSE.txt --force
hinagata license ISC -o - > LICENSE
hinagata license --list
```

| Option         | Description                                               |
| -------------- | --------------------------------------------------------- |
| `[LICENSE]`    | SPDX identifier, case-insensitive. Asked when omitted.    |
| `-a, --author` | Copyright holder. Defaults to `git config user.name`.     |
| `-y, --year`   | Year or range such as `2020-2026`. Defaults to this year. |
| `-o, --output` | File to write, or `-` for stdout. Defaults to `LICENSE`.  |
| `-f, --force`  | Overwrite an existing file without asking.                |
| `-l, --list`   | List the available licenses.                              |

### Gitignore

```sh
hinagata gitignore Python Linux VisualStudioCode
hinagata gitignore Node --append
hinagata gitignore --list
```

Combine as many templates as you like. Each one is written under a
`### Name ###` header. With `--append`, templates already present in the file
are skipped, so the command is safe to run again.

| Option          | Description                                                           |
| --------------- | --------------------------------------------------------------------- |
| `[TEMPLATE]...` | Template names, case-insensitive. Asked when omitted.                 |
| `-o, --output`  | File to write, or `-` for stdout. Defaults to `.gitignore`.           |
| `-f, --force`   | Replace an existing file without asking.                              |
| `--append`      | Add the templates the file is missing, leaving everything else alone. |
| `-l, --list`    | List the available templates.                                         |

## Short alias

Every install also provides `hina`, which behaves exactly like `hinagata`:

```sh
hina license MIT -a "Ada Lovelace"
hina gitignore Python
```

Without installing, use `uvx --from hinagata hina`, since `uvx hina` would fetch
an unrelated package.

## Development

Install the project with `uv sync`, then run the test suite with
`uv run pytest`.
