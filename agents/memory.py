"""Helpers for initializing synthetic agent rationale memory and explanation traces."""

from __future__ import annotations

from agents.models import ConfidenceLevel, MemoryEntry


def make_memory_entry(memory_id: str, statement: str, source: str, confidence: ConfidenceLevel) -> MemoryEntry:
    """Create a deterministic memory entry for generation-time explanations."""

    return MemoryEntry(
        memory_id=memory_id,
        statement=statement,
        source=source,
        confidence=confidence,
    )


def build_initial_explanation_trace(statements: list[tuple[str, str, str, ConfidenceLevel]]) -> list[MemoryEntry]:
    """Convert simple generation statements into ordered explanation entries."""

    return [make_memory_entry(*statement) for statement in statements]