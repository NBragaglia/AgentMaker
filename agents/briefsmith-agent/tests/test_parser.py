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

    assert any("diligence kickoff" in item.lower() for item in brief.situation)
    assert any("margin expanded" in item.lower() for item in brief.key_findings)
    assert any("customer concentration" in item.lower() for item in brief.risks)
    assert any("?" in item for item in brief.open_questions)
    assert any("owner" in item.lower() for item in brief.next_steps)


def test_parser_uses_fallback_for_unclassified_lines() -> None:
    raw = """
    Alpha datapoint from interview
    Beta datapoint from workshop
    """
    brief = parse_notes(raw, Mode.CLIENT)

    assert any("alpha datapoint from interview" in item.lower() for item in brief.key_findings)
    assert brief.situation[0] == PLACEHOLDER


def test_parser_inserts_placeholders_for_missing_sections() -> None:
    brief = parse_notes("Single unclassified note", Mode.INVESTMENT)

    assert brief.key_findings[0] == "Single unclassified note."
    assert brief.situation[0] == PLACEHOLDER
    assert brief.risks[0] == PLACEHOLDER
    assert brief.open_questions[0] == PLACEHOLDER
    assert brief.next_steps[0] == PLACEHOLDER


def test_parser_handles_windows_newlines_and_question_only_lines() -> None:
    raw = "Why is EBITDA down?\r\nWhat changed in pricing?\r\n"
    brief = parse_notes(raw, Mode.INTERNAL)

    assert brief.open_questions == ["Why is EBITDA down?", "What changed in pricing?"]


def test_parser_cleans_transcript_timestamps_and_speakers() -> None:
    raw = """
    [10:02 AM] Alex: Background: diligence kickoff and scope alignment
    10:05 - 10:06 Speaker 2: Finding: churn is concentrated in SMB
    10:07 AM Moderator: Risk: implementation timeline is compressed
    """
    brief = parse_notes(raw, Mode.INTERNAL)

    assert "Diligence kickoff and scope alignment." in brief.situation
    assert "Churn is concentrated in SMB." in brief.key_findings
    assert "Implementation timeline is compressed." in brief.risks


def test_parser_drops_transcript_metadata_lines() -> None:
    raw = """
    Meeting started
    Recording started
    Attendees: Alex, Sam
    """
    brief = parse_notes(raw, Mode.CLIENT)

    assert brief.situation[0] == PLACEHOLDER
    assert brief.key_findings[0] == PLACEHOLDER


def test_parser_limits_section_size_for_large_inputs() -> None:
    raw = "\n".join([f"Finding: datapoint {idx} improved by 5%" for idx in range(20)])
    brief = parse_notes(raw, Mode.CLIENT)

    assert len(brief.key_findings) <= 4


def test_parser_respects_explicit_max_bullets_override() -> None:
    raw = "\n".join([f"Finding: datapoint {idx} improved by 5%" for idx in range(20)])
    brief = parse_notes(raw, Mode.INVESTMENT, max_bullets=2)

    assert len(brief.key_findings) <= 2


def test_parser_tracks_source_lines() -> None:
    raw = "Background: kickoff\nFinding: margin improved\n"
    brief = parse_notes(raw, Mode.INTERNAL)

    assert "Background: kickoff" in brief.source_lines
