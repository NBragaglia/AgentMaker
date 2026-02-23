from __future__ import annotations

from pathlib import Path

from stock_master.cli import main
from stock_master.prompt_assets import (
    CONSTRAINTS_QUESTIONNAIRE_TEMPLATE,
    IMPLEMENTATION_BRIEF_TEMPLATE,
)


def test_cli_default_message(capsys) -> None:
    exit_code = main([])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "scaffold is ready" in captured.out
    assert "init-brief" in captured.out
    assert "bootstrap" in captured.out


def test_cli_version(capsys) -> None:
    exit_code = main(["--version"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out.strip() == "0.1.0"


def test_show_prompt_command(capsys) -> None:
    exit_code = main(["show-prompt"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Stock Master — System Prompt Blueprint" in captured.out
    assert "Final response requirement" in captured.out


def test_init_brief_writes_default_template(tmp_path: Path, capsys) -> None:
    out_file = tmp_path / "brief.md"

    exit_code = main(["init-brief", "--output", str(out_file)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert out_file.exists()
    assert out_file.read_text(encoding="utf-8") == IMPLEMENTATION_BRIEF_TEMPLATE
    assert str(out_file) in captured.out


def test_init_brief_blocks_overwrite_without_force(tmp_path: Path, capsys) -> None:
    out_file = tmp_path / "brief.md"
    out_file.write_text("existing", encoding="utf-8")

    exit_code = main(["init-brief", "--output", str(out_file)])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Refusing to overwrite" in captured.out
    assert out_file.read_text(encoding="utf-8") == "existing"


def test_init_brief_force_overwrites_existing_file(tmp_path: Path) -> None:
    out_file = tmp_path / "brief.md"
    out_file.write_text("old", encoding="utf-8")

    exit_code = main(["init-brief", "--output", str(out_file), "--force"])

    assert exit_code == 0
    assert out_file.read_text(encoding="utf-8") == IMPLEMENTATION_BRIEF_TEMPLATE


def test_bootstrap_creates_all_assets(tmp_path: Path) -> None:
    exit_code = main(["bootstrap", "--output-dir", str(tmp_path)])

    assert exit_code == 0
    assert (tmp_path / "AGENT_PROMPT.md").exists()
    assert (tmp_path / "stock_master_implementation_brief.md").exists()
    assert (tmp_path / "stock_master_constraints.json").exists()


def test_bootstrap_refuses_to_overwrite_without_force(tmp_path: Path, capsys) -> None:
    (tmp_path / "AGENT_PROMPT.md").write_text("old", encoding="utf-8")

    exit_code = main(["bootstrap", "--output-dir", str(tmp_path)])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Refusing to overwrite" in captured.out


def test_bootstrap_force_overwrites_existing_assets(tmp_path: Path) -> None:
    prompt_path = tmp_path / "AGENT_PROMPT.md"
    constraints_path = tmp_path / "stock_master_constraints.json"

    prompt_path.write_text("old", encoding="utf-8")
    constraints_path.write_text("{}", encoding="utf-8")

    exit_code = main(["bootstrap", "--output-dir", str(tmp_path), "--force"])

    assert exit_code == 0
    assert "Stock Master — System Prompt Blueprint" in prompt_path.read_text(encoding="utf-8")
    assert constraints_path.read_text(encoding="utf-8") == CONSTRAINTS_QUESTIONNAIRE_TEMPLATE
