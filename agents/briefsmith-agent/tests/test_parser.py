from briefsmith_agent.models import Mode
from briefsmith_agent.parser import PLACEHOLDER, parse_notes


def test_parser_classifies_keywords_into_sections() -> None:
    raw = """
    - Background: Q1 diligence kickoff for target.
    - Key finding: margin expanded in two segments.
    - Risk: customer concentration remains high.
    - Open question: is churn risk elevated?
    - Next step: assign owner for management interview.
    """
    brief = parse_notes(raw, Mode.INTERNAL)

    assert any("Background" in item for item in brief.situation)
    assert any("finding" in item.lower() for item in brief.key_findings)
    assert any("Risk" in item for item in brief.risks)
    assert any("?" in item for item in brief.open_questions)
    assert any("owner" in item.lower() for item in brief.next_steps)


def test_parser_uses_fallback_for_unclassified_lines() -> None:
    raw = """
    Alpha datapoint from interview
    Beta datapoint from workshop
    """
    brief = parse_notes(raw, Mode.CLIENT)

    assert "Alpha datapoint from interview" in brief.key_findings
    assert "Beta datapoint from workshop" in brief.situation


def test_parser_inserts_placeholders_for_missing_sections() -> None:
    brief = parse_notes("Single unclassified note", Mode.INVESTMENT)

    assert brief.key_findings[0] == "Single unclassified note"
    assert brief.situation[0] == PLACEHOLDER
    assert brief.risks[0] == PLACEHOLDER
    assert brief.open_questions[0] == PLACEHOLDER
    assert brief.next_steps[0] == PLACEHOLDER


def test_parser_handles_windows_newlines_and_question_only_lines() -> None:
    raw = "Why is EBITDA down?\r\nWhat changed in pricing?\r\n"
    brief = parse_notes(raw, Mode.INTERNAL)

    assert brief.open_questions == ["Why is EBITDA down?", "What changed in pricing?"]
