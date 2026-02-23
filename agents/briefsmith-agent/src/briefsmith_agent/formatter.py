"""Markdown formatter for generated briefs."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

from .models import Brief, Mode

_MODE_DESCRIPTIONS = {
    Mode.INTERNAL: "Internal operational brief with candid execution focus.",
    Mode.CLIENT: "Client-ready brief emphasizing outcomes and clarity.",
    Mode.INVESTMENT: "Investment diligence brief focused on value and risk framing.",
}


def format_markdown(
    brief: Brief,
    mode: Mode,
    source_path: Path,
    max_ktas: int = 4,
    email_ready: bool = False,
) -> str:
    """Format brief sections into markdown output."""
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines: list[str] = [
        "# Briefsmith Work Brief",
        "",
        f"- Mode: `{mode.value}`",
        f"- Source: `{source_path}`",
        f"- Generated: `{generated_at}`",
        f"- Framing: {_MODE_DESCRIPTIONS[mode]}",
        "",
    ]

    ktas = _build_ktas(brief, max_ktas=max_ktas)
    _append_section(lines, "Key Takeaways (KTAs)", ktas)
    _append_section(lines, "KTA Source Snippets", _build_kta_citations(ktas, brief.source_lines))
    _append_section(lines, "Situation", brief.situation)
    _append_section(lines, "Key Findings", brief.key_findings)
    _append_section(lines, "Risks", brief.risks)
    _append_section(lines, "Open Questions", brief.open_questions)
    _append_section(lines, "Next Steps", brief.next_steps)
    if email_ready:
        _append_section(lines, "Team Update Email Draft", _build_email_draft(brief, mode))

    return "\n".join(lines).strip() + "\n"


def _append_section(lines: list[str], title: str, items: list[str]) -> None:
    """Append a heading and bullets for one section."""
    lines.append(f"## {title}")
    for item in items:
        lines.append(f"- {item}")
    lines.append("")


def _build_ktas(brief: Brief, max_ktas: int) -> list[str]:
    """Build concise top-level takeaways from findings and risks."""
    kta_candidates = brief.key_findings[:3] + brief.risks[:2]
    unique: list[str] = []
    seen: set[str] = set()
    for line in kta_candidates:
        normalized = line.lower().strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique.append(line)
    return unique[:max_ktas] if unique else ["No clear input provided."]


def _build_kta_citations(ktas: list[str], source_lines: list[str]) -> list[str]:
    """Create short source snippets for each KTA using lexical overlap."""
    if not source_lines:
        return ["No source snippets available."]
    citations: list[str] = []
    for idx, kta in enumerate(ktas, start=1):
        best = _best_source_line(kta, source_lines)
        snippet = _truncate(best, 170) if best else "No matching source line found."
        citations.append(f"KTA {idx}: {snippet}")
    return citations


def _best_source_line(kta: str, source_lines: list[str]) -> str:
    """Select source line with highest token overlap for the KTA."""
    kta_tokens = _tokenize(kta)
    best_line = ""
    best_score = -1.0
    for line in source_lines:
        line_tokens = _tokenize(line)
        if not line_tokens:
            continue
        overlap = len(kta_tokens & line_tokens)
        score = overlap / max(1, len(kta_tokens))
        if score > best_score:
            best_score = score
            best_line = line
    return best_line


def _tokenize(text: str) -> set[str]:
    """Tokenize text into lowercase meaningful words."""
    return {token.lower() for token in re.findall(r"[A-Za-z0-9]+", text) if len(token) >= 3}


def _truncate(text: str, max_len: int) -> str:
    """Truncate text to a max length with ellipsis."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


def _build_email_draft(brief: Brief, mode: Mode) -> list[str]:
    """Build a concise team update email draft from the brief."""
    subject = {
        Mode.INTERNAL: "Subject: Internal Update - Briefsmith Summary",
        Mode.CLIENT: "Subject: Client Update - Key Findings and Next Steps",
        Mode.INVESTMENT: "Subject: Investment Update - Diligence Highlights and Risks",
    }[mode]

    finding = brief.key_findings[0] if brief.key_findings else "No key findings available."
    risk = brief.risks[0] if brief.risks else "No clear risks identified."
    next_step = brief.next_steps[0] if brief.next_steps else "No next steps captured."

    return [
        subject,
        "Hi team,",
        f"Quick update: {finding}",
        f"Primary risk to watch: {risk}",
        f"Immediate next step: {next_step}",
        "Please reply with additions or corrections before distribution.",
        "Thanks,",
        "[Your Name]",
    ]
