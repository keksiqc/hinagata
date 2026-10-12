from __future__ import annotations

from template_pypackage.cli import main


def test_main(capsys) -> None:
    main([])

    assert capsys.readouterr().out == "Hello from template-pypackage!\n"
