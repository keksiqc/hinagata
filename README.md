# licensd

A lightweight license generator CLI. Pick a license from a filterable list,
confirm the author and year, and get a `LICENSE` file.

## Usage

```sh
uv run licensd
```

Run without arguments to choose a license interactively. Everything can also be
passed as flags, which skips the matching prompt and makes the command
scriptable:

```sh
licensd MIT --author "Ada Lovelace" --year 2026
licensd Apache-2.0 --output LICENSE.txt --force
licensd ISC -o - > LICENSE
licensd --list
```

| Option           | Description                                              |
| ---------------- | -------------------------------------------------------- |
| `[LICENSE]`      | SPDX identifier, case-insensitive. Asked when omitted.   |
| `-a, --author`   | Copyright holder. Defaults to `git config user.name`.    |
| `-y, --year`     | Year or range such as `2020-2026`. Defaults to this year. |
| `-o, --output`   | File to write, or `-` for stdout. Defaults to `LICENSE`. |
| `-f, --force`    | Overwrite an existing file without asking.               |
| `-l, --list`     | List the available licenses.                             |

Author and year are only asked for licenses whose text contains them (MIT, ISC,
BSD, 0BSD). The others, such as the GPL family and Apache-2.0, are written
verbatim.

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
