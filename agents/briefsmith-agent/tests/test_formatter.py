from pathlib import Path

from briefsmith_agent.formatter import format_markdown
from briefsmith_agent.models import Brief, Mode


def _sample_brief() -> Brief:
    return Brief(
        situation=["Current state summary"],
        key_findings=["Finding one"],
        risks=["Key risk"],
        open_questions=["Open item?"],
        next_steps=["Do next thing"],
    )


def test_formatter_includes_sections_in_required_order() -> None:
    markdown = format_markdown(_sample_brief(), Mode.CLIENT, Path("notes.txt"))

    situation_idx = markdown.index("## Situation")
    findings_idx = markdown.index("## Key Findings")
    risks_idx = markdown.index("## Risks")
    questions_idx = markdown.index("## Open Questions")
    next_steps_idx = markdown.index("## Next Steps")

    assert situation_idx < findings_idx < risks_idx < questions_idx < next_steps_idx


def test_formatter_includes_mode_specific_framing() -> None:
    internal_md = format_markdown(_sample_brief(), Mode.INTERNAL, Path("a.txt"))
    client_md = format_markdown(_sample_brief(), Mode.CLIENT, Path("a.txt"))
    invest_md = format_markdown(_sample_brief(), Mode.INVESTMENT, Path("a.txt"))

    assert "Internal operational brief" in internal_md
    assert "Client-ready brief" in client_md
    assert "Investment diligence brief" in invest_md
