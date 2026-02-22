from __AGENT_PACKAGE__.cli import main


def test_cli_default_message(capsys) -> None:
    exit_code = main([])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "scaffold is ready" in captured.out


def test_cli_version(capsys) -> None:
    exit_code = main(["--version"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out.strip() == "0.1.0"
