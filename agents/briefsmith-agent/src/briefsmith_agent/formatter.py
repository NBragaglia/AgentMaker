"""Markdown formatter for generated briefs."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .models import Brief, Mode

_MODE_DESCRIPTIONS = {
    Mode.INTERNAL: "Internal operational brief with candid execution focus.",
    Mode.CLIENT: "Client-ready brief emphasizing outcomes and clarity.",
    Mode.INVESTMENT: "Investment diligence brief focused on value and risk framing.",
}


def format_markdown(brief: Brief, mode: Mode, source_path: Path) -> str:
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

    _append_section(lines, "Key Takeaways (KTAs)", _build_ktas(brief))
    _append_section(lines, "Situation", brief.situation)
    _append_section(lines, "Key Findings", brief.key_findings)
    _append_section(lines, "Risks", brief.risks)
    _append_section(lines, "Open Questions", brief.open_questions)
    _append_section(lines, "Next Steps", brief.next_steps)

    return "\n".join(lines).strip() + "\n"


def _append_section(lines: list[str], title: str, items: list[str]) -> None:
    """Append a heading and bullets for one section."""
    lines.append(f"## {title}")
    for item in items:
        lines.append(f"- {item}")
    lines.append("")


def _build_ktas(brief: Brief) -> list[str]:
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
    return unique[:4] if unique else ["No clear input provided."]
