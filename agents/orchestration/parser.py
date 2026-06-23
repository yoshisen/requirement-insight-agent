"""Structured output parsing for survey and interview responses."""

from __future__ import annotations

import json

from rag.models import CitationTrace
from simulations.models import (
    AgentResponseMetadata,
    AgentResponseRecord,
    ExplanationTraceStep,
    PriceReaction,
)


def parse_agent_response_text(
    *,
    response_text: str,
    response_id: str,
    scenario_id: str,
    agent_id: str,
    metadata: AgentResponseMetadata,
) -> AgentResponseRecord:
    """Parse JSON text returned by a provider into a validated response record."""

    payload = _extract_json_payload(response_text)

    return AgentResponseRecord(
        response_id=response_id,
        scenario_id=scenario_id,
        agent_id=agent_id,
        purchase_intent=payload["purchase_intent"],
        reasons=payload.get("reasons", []),
        objections=payload.get("objections", []),
        price_reaction=PriceReaction.model_validate(payload.get("price_reaction", {})),
        preferred_channel=payload["preferred_channel"],
        uncertainty=payload["uncertainty"],
        confidence=payload["confidence"],
        citations=[CitationTrace.model_validate(item) for item in payload.get("citations", [])],
        grounding_refs=payload.get("grounding_refs", []),
        explanation_trace=[
            ExplanationTraceStep.model_validate(item) for item in payload.get("explanation_trace", [])
        ],
        follow_up_summary=payload.get("follow_up_summary"),
        metadata=metadata,
    )


def _extract_json_payload(response_text: str) -> dict:
    text = response_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)