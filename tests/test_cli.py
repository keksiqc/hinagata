from __future__ import annotations

from licensd.cli import main


def test_main(capsys) -> None:
    main([])

    assert capsys.readouterr().out == "Hello from licensd!\n"
