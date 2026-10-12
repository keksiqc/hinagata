# licensd

A lightweight license generator CLI. Pick a license from a filterable list,
confirm the author and year, and get a `LICENSE` file.

## Usage

Run `licensd` to choose a license interactively, or pass everything as flags:

```sh
licensd MIT --author "Ada Lovelace" --year 2026
licensd --list
```

See the project README for the full list of options.

## Development

Install the project with `uv sync`, then run the test suite with
`uv run pytest`.
