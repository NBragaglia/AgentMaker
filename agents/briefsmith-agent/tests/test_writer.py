from pathlib import Path

from briefsmith_agent.models import Mode
from briefsmith_agent.writer import save_markdown


def test_writer_creates_directory_and_writes_file(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs"
    output_path = save_markdown("# Test\n", Mode.INTERNAL, output_dir)

    assert output_dir.exists()
    assert output_path.exists()
    assert output_path.name.startswith("brief_internal_")
    assert output_path.suffix == ".md"
    assert output_path.read_text(encoding="utf-8") == "# Test\n"
