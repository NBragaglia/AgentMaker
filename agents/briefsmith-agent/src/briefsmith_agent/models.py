"""Shared models for brief generation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Mode(str, Enum):
    """Supported brief generation modes."""

    INTERNAL = "internal"
    CLIENT = "client"
    INVESTMENT = "investment"


@dataclass(slots=True)
class Brief:
    """Structured brief sections."""

    situation: list[str]
    key_findings: list[str]
    risks: list[str]
    open_questions: list[str]
    next_steps: list[str]
    source_lines: list[str]
