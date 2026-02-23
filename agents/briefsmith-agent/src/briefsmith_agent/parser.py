"""Rule-based parser for messy notes."""

from __future__ import annotations

import re

from .models import Brief, Mode

PLACEHOLDER = "No clear input provided."
_BULLET_PREFIX_RE = re.compile(r"^\s*(?:[-*]\s+|\d+[.)]\s+)")
_TIMESTAMP_TOKEN_RE = re.compile(
    r"^\s*\[?\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?\]?\s*(?:-\s*)?"
)
_METADATA_LINE_RE = re.compile(
    r"^\s*(?:meeting (?:started|ended)|recording (?:started|stopped)|"
    r"joined the meeting|left the meeting|transcript(?:ion)?|attendees?:)",
    re.IGNORECASE,
)
_FILLER_WORD_RE = re.compile(r"\b(?:um+|uh+|like|you know|sort of|kind of)\b", re.IGNORECASE)
_SPEAKER_LABEL_RE = re.compile(r"^(?:speaker \d+|host|moderator|me)$", re.IGNORECASE)
_SPEAKER_NAME_RE = re.compile(r"^[A-Z][a-z]+(?: [A-Z][a-z]+){0,2}$")
_SECTION_PREFIX_WORDS = {"background", "context", "risk", "finding", "open", "next", "situation"}

_SITUATION_KEYWORDS = {
    "context",
    "background",
    "current",
    "status",
    "situation",
    "today",
    "scope",
    "overview",
    "baseline",
}

_FINDINGS_KEYWORDS = {
    "finding",
    "findings",
    "insight",
    "insights",
    "result",
    "results",
    "observed",
    "analysis",
    "evidence",
    "data",
}

_RISK_KEYWORDS = {
    "risk",
    "risks",
    "blocker",
    "issue",
    "issues",
    "constraint",
    "constraints",
    "downside",
    "exposure",
    "concern",
    "challenge",
}

_QUESTION_KEYWORDS = {
    "question",
    "questions",
    "unknown",
    "unknowns",
    "assumption",
    "assumptions",
    "clarify",
    "unclear",
}

_NEXT_STEPS_KEYWORDS = {
    "next",
    "action",
    "actions",
    "owner",
    "timeline",
    "follow-up",
    "followup",
    "plan",
    "deliver",
    "due",
}


def parse_notes(raw_text: str, mode: Mode) -> Brief:
    """Parse unstructured notes into a structured brief object."""
    _ = mode
    lines = _normalize_lines(raw_text)

    buckets: dict[str, list[str]] = {
        "situation": [],
        "key_findings": [],
        "risks": [],
        "open_questions": [],
        "next_steps": [],
    }
    unclassified: list[str] = []

    for line in lines:
        section = _classify_line(line)
        if section is None:
            unclassified.append(line)
            continue
        buckets[section].append(line)

    if unclassified:
        buckets["key_findings"].append(unclassified[0])
        if len(unclassified) > 1:
            buckets["situation"].extend(unclassified[1:])

    _ensure_placeholders(buckets)

    return Brief(
        situation=buckets["situation"],
        key_findings=buckets["key_findings"],
        risks=buckets["risks"],
        open_questions=buckets["open_questions"],
        next_steps=buckets["next_steps"],
    )


def _normalize_lines(raw_text: str) -> list[str]:
    """Normalize text to meaningful non-empty lines."""
    normalized: list[str] = []
    for raw_line in raw_text.splitlines():
        cleaned = _clean_transcript_line(raw_line)
        if not cleaned:
            continue
        normalized.append(cleaned)
    return normalized


def _contains_any_keyword(line: str, keywords: set[str]) -> bool:
    """Return True when line contains at least one keyword as a whole word."""
    lower = line.lower()
    return any(re.search(rf"\b{re.escape(keyword)}\b", lower) for keyword in keywords)


def _classify_line(line: str) -> str | None:
    """Classify line to a section key."""
    if "?" in line or _contains_any_keyword(line, _QUESTION_KEYWORDS):
        return "open_questions"
    if _contains_any_keyword(line, _RISK_KEYWORDS):
        return "risks"
    if _contains_any_keyword(line, _NEXT_STEPS_KEYWORDS):
        return "next_steps"
    if _contains_any_keyword(line, _SITUATION_KEYWORDS):
        return "situation"
    if _contains_any_keyword(line, _FINDINGS_KEYWORDS):
        return "key_findings"
    return None


def _ensure_placeholders(buckets: dict[str, list[str]]) -> None:
    """Ensure each required section has at least one bullet."""
    for items in buckets.values():
        if not items:
            items.append(PLACEHOLDER)


def _clean_transcript_line(raw_line: str) -> str:
    """Clean common transcript noise while preserving meaningful note content."""
    stripped = raw_line.strip()
    if not stripped or _METADATA_LINE_RE.search(stripped):
        return ""

    cleaned = _BULLET_PREFIX_RE.sub("", stripped).strip()
    while True:
        updated = _TIMESTAMP_TOKEN_RE.sub("", cleaned).strip()
        if updated == cleaned:
            break
        cleaned = updated
    cleaned = _strip_speaker_prefix(cleaned)
    cleaned = _FILLER_WORD_RE.sub(" ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -|:")
    return cleaned


def _strip_speaker_prefix(line: str) -> str:
    """Strip transcript speaker prefixes while preserving real note headings."""
    if ":" not in line:
        return line
    prefix, remainder = line.split(":", 1)
    normalized = prefix.strip()
    if not normalized:
        return line

    head_word = normalized.split()[0].lower()
    if head_word in _SECTION_PREFIX_WORDS:
        return line
    if _SPEAKER_LABEL_RE.match(normalized) or _SPEAKER_NAME_RE.match(normalized):
        return remainder.strip()
    return line
