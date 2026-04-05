from __future__ import annotations

import main


def test_main_prints_expected_greeting(capsys):
    main.main()
    out = capsys.readouterr().out
    assert out.strip() == "Hello from summary!"
