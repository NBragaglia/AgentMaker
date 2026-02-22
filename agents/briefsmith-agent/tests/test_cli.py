from pathlib import Path

from briefsmith_agent.cli import main


def test_cli_valid_run_writes_markdown(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "notes.txt"
    input_path.write_text("Risk: timeline slip\n", encoding="utf-8")
    output_dir = tmp_path / "outputs"

    exit_code = main([str(input_path), "--mode", "internal", "--output-dir", str(output_dir)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Brief generated:" in captured.out
    files = list(output_dir.glob("brief_internal_*.md"))
    assert len(files) == 1


def test_cli_rejects_missing_file(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "missing.txt"
    exit_code = main([str(missing), "--mode", "client"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Input file not found" in captured.err


def test_cli_rejects_non_txt_file(tmp_path: Path, capsys) -> None:
    bad_file = tmp_path / "notes.md"
    bad_file.write_text("content", encoding="utf-8")

    exit_code = main([str(bad_file), "--mode", "investment"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Expected a .txt file" in captured.err


def test_cli_rejects_empty_file(tmp_path: Path, capsys) -> None:
    empty_file = tmp_path / "notes.txt"
    empty_file.write_text("   \n\n", encoding="utf-8")

    exit_code = main([str(empty_file), "--mode", "internal"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Input file is empty" in captured.err


def test_cli_invalid_mode_returns_parser_error(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "notes.txt"
    input_path.write_text("Something", encoding="utf-8")

    exit_code = main([str(input_path), "--mode", "badmode"])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "invalid choice" in captured.err.lower()
