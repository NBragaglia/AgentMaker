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
_DOCUMENT_NOISE_RE = re.compile(
    r"^\s*(?:prepared by\b|framing the core question\b|table of contents\b|"
    r"hoa management\s*&\s*software:\s*\d{4}\s*investment landscape\b)",
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

_SECTION_LIMITS = {
    Mode.INTERNAL: {"situation": 4, "key_findings": 5, "risks": 4, "open_questions": 4, "next_steps": 5},
    Mode.CLIENT: {"situation": 3, "key_findings": 4, "risks": 3, "open_questions": 3, "next_steps": 4},
    Mode.INVESTMENT: {"situation": 3, "key_findings": 5, "risks": 4, "open_questions": 3, "next_steps": 4},
}


def parse_notes(raw_text: str, mode: Mode) -> Brief:
    """Parse unstructured notes into a concise structured brief object."""
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
        buckets["key_findings"].extend(unclassified)

    _condense_buckets(buckets, mode)

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


def _condense_buckets(buckets: dict[str, list[str]], mode: Mode) -> None:
    """Deduplicate and keep only the most salient bullets per section."""
    limits = _SECTION_LIMITS[mode]
    for section, items in buckets.items():
        if not items:
            continue
        deduped = _dedupe_lines(items)
        ranked = sorted(deduped, key=lambda line: _salience_score(line, section), reverse=True)
        concise = [_to_sendable_bullet(line) for line in ranked[: limits[section]]]
        buckets[section] = concise


def _dedupe_lines(lines: list[str]) -> list[str]:
    """Deduplicate near-identical lines using alphanumeric normalization."""
    seen: set[str] = set()
    deduped: list[str] = []
    for line in lines:
        key = re.sub(r"[^a-z0-9]+", "", line.lower())
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(line)
    return deduped


def _salience_score(line: str, section: str) -> float:
    """Compute a heuristic relevance score for ranking candidate bullets."""
    lower = line.lower()
    score = 1.0

    if any(char.isdigit() for char in line):
        score += 1.0
    if len(line) < 140:
        score += 0.5
    if " vs " in lower or "%" in line:
        score += 0.5

    keyword_map = {
        "situation": _SITUATION_KEYWORDS,
        "key_findings": _FINDINGS_KEYWORDS,
        "risks": _RISK_KEYWORDS,
        "open_questions": _QUESTION_KEYWORDS,
        "next_steps": _NEXT_STEPS_KEYWORDS,
    }
    section_keywords = keyword_map[section]
    score += sum(0.4 for kw in section_keywords if re.search(rf"\b{re.escape(kw)}\b", lower))
    return score


def _to_sendable_bullet(line: str) -> str:
    """Normalize a line into concise send-ready bullet phrasing."""
    cleaned = re.sub(r"^(?:background|context|finding|risk|open question|next step)\s*:\s*", "", line, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    if not cleaned:
        return line
    cleaned = _compress_long_bullet(cleaned)
    if cleaned and cleaned[-1] not in ".!?":
        cleaned += "."
    return cleaned[0].upper() + cleaned[1:] if cleaned else line


def _clean_transcript_line(raw_line: str) -> str:
    """Clean common transcript noise while preserving meaningful note content."""
    stripped = raw_line.strip()
    if not stripped or _METADATA_LINE_RE.search(stripped) or _DOCUMENT_NOISE_RE.search(stripped):
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
    if _is_low_signal_heading(cleaned):
        return ""
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


def _compress_long_bullet(text: str) -> str:
    """Compress very long bullets into one concise sentence."""
    if len(text) <= 190:
        return text
    first_sentence = re.split(r"(?<=[.!?])\s+", text)[0].strip()
    if 35 <= len(first_sentence) <= 190:
        return first_sentence
    words = text.split()
    if len(words) <= 28:
        return text
    return " ".join(words[:28]).rstrip(",;:") + "..."


def _is_low_signal_heading(line: str) -> bool:
    """Detect heading-like lines that should not become bullets."""
    if not line:
        return True
    alpha_words = [w for w in re.split(r"\s+", line) if re.search(r"[A-Za-z]", w)]
    if 0 < len(alpha_words) <= 5 and all(w[:1].isupper() for w in alpha_words):
        return True
    return False
