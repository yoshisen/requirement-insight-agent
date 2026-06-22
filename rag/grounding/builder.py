"""Build grounding contexts from retrieved chunks."""

from __future__ import annotations

import uuid

from rag.models import GroundingContext, RetrievedChunk
from rag.retrieval.search import RetrievalQuery


def build_grounding_context(query: RetrievalQuery, chunks: list[RetrievedChunk]) -> GroundingContext:
    """Create a grounding context and mark uncertainty when evidence is weak."""

    notes: list[str] = []
    if not chunks:
        overall_uncertainty = "high"
        notes.append("No grounded chunks were retrieved for this query.")
    else:
        top_score = max(chunk.score for chunk in chunks)
        if len(chunks) < 2 or top_score < 0.35:
            overall_uncertainty = "high"
            notes.append("Evidence is sparse or weak; treat downstream answers as uncertain.")
        elif top_score < 0.55:
            overall_uncertainty = "medium"
            notes.append("Grounding evidence is usable but not strong.")
        else:
            overall_uncertainty = "low"

    return GroundingContext(
        context_id=f"ctx-{uuid.uuid4().hex[:8]}",
        scenario_id=query.scenario_id,
        chunks=chunks,
        overall_uncertainty=overall_uncertainty,
        notes=notes,
    )