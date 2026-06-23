"""Prompt construction for survey and interview runner flows."""

from __future__ import annotations

import json

from agents.models import SyntheticConsumerAgent
from rag.models import GroundingContext
from requirement_insight_agent.core.providers.models import ChatMessage, ChatRequest
from simulations.models import PromptSpec, ScenarioDefinition


def build_chat_request(
    *,
    agent: SyntheticConsumerAgent,
    scenario: ScenarioDefinition,
    prompt_spec: PromptSpec,
    grounding_context: GroundingContext,
    model_name: str,
    temperature: float,
    max_tokens: int | None,
    structured_response: dict | None = None,
    follow_up_context: dict | None = None,
) -> ChatRequest:
    """Build a provider-agnostic chat request for one agent execution."""

    system_lines = list(prompt_spec.instructions)
    system_lines.append("あなたは実在人物ではなく synthetic consumer agent として応答してください。")
    system_lines.append("根拠不足時は保留し、不確実性を上げてください。")
    system_lines.append("必ず JSON だけを返してください。")

    payload = {
        "scenario": scenario.model_dump(mode="json"),
        "agent_profile": agent.model_dump(mode="json"),
        "grounding_context": grounding_context.model_dump(mode="json"),
        "questions": [question.model_dump(mode="json") for question in prompt_spec.questions],
        "output_schema_hint": prompt_spec.output_schema_hint,
    }
    if follow_up_context is not None:
        payload["follow_up_context"] = follow_up_context

    return ChatRequest(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            ChatMessage(role="system", content="\n".join(system_lines)),
            ChatMessage(role="user", content=json.dumps(payload, ensure_ascii=False, indent=2)),
        ],
        metadata={"structured_response": structured_response} if structured_response is not None else {},
    )