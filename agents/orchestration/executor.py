"""Per-agent survey and interview execution logic."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from agents.models import SyntheticConsumerAgent
from rag.models import GroundingContext
from requirement_insight_agent.core.providers.exceptions import ProviderError
from requirement_insight_agent.core.providers.factory import ProviderStack
from simulations.models import AgentResponseMetadata, AgentResponseRecord, PromptSpec, ScenarioDefinition

from .parser import parse_agent_response_text
from .prompt_builder import build_chat_request


def execute_prompt_for_agent(
    *,
    agent: SyntheticConsumerAgent,
    scenario: ScenarioDefinition,
    prompt_spec: PromptSpec,
    grounding_context: GroundingContext,
    provider_stack: ProviderStack,
    max_retries: int,
    temperature: float,
    max_tokens: int | None,
) -> AgentResponseRecord:
    """Execute one prompt spec for one synthetic agent with retry support."""

    provider_name = getattr(provider_stack.chat, "provider_name", "unknown")
    provider_model = getattr(provider_stack.chat, "config", None)
    provider_model_name = getattr(provider_model, "chat_model", "unknown-model")

    last_error: Exception | None = None
    follow_up_summary: str | None = None

    for attempt in range(1, max_retries + 2):
        try:
            request = build_chat_request(
                agent=agent,
                scenario=scenario,
                prompt_spec=prompt_spec,
                grounding_context=grounding_context,
                model_name=provider_model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                structured_response=_build_local_structured_response(
                    agent=agent,
                    scenario=scenario,
                    grounding_context=grounding_context,
                    mode=prompt_spec.mode,
                )
                if provider_name == "local"
                else None,
            )
            response = provider_stack.chat.complete(request)

            metadata = AgentResponseMetadata(
                provider_name=response.provider,
                provider_model=response.model,
                prompt_spec_id=prompt_spec.prompt_spec_id,
                attempt_count=attempt,
                mode=prompt_spec.mode,
                generated_at=datetime.now(timezone.utc),
            )
            parsed = parse_agent_response_text(
                response_text=response.output_text,
                response_id=f"resp-{uuid.uuid4().hex[:8]}",
                scenario_id=scenario.scenario_id,
                agent_id=agent.agent_id,
                metadata=metadata,
            )

            if prompt_spec.mode == "interview_multi_turn":
                follow_up_summary = _run_follow_up(
                    agent=agent,
                    scenario=scenario,
                    prompt_spec=prompt_spec,
                    grounding_context=grounding_context,
                    provider_stack=provider_stack,
                    prior_response=parsed,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    provider_model_name=provider_model_name,
                )
                parsed.follow_up_summary = follow_up_summary

            return parsed
        except Exception as exc:  # noqa: BLE001
            last_error = exc

    if isinstance(last_error, Exception):
        raise last_error
    raise ProviderError("agent execution failed without a specific exception")


def _run_follow_up(
    *,
    agent: SyntheticConsumerAgent,
    scenario: ScenarioDefinition,
    prompt_spec: PromptSpec,
    grounding_context: GroundingContext,
    provider_stack: ProviderStack,
    prior_response: AgentResponseRecord,
    temperature: float,
    max_tokens: int | None,
    provider_model_name: str,
) -> str:
    provider_name = getattr(provider_stack.chat, "provider_name", "unknown")
    follow_up_context = {
        "prior_reasons": prior_response.reasons,
        "prior_objections": prior_response.objections,
        "purchase_intent": prior_response.purchase_intent,
    }
    structured_response = (
        {
            "purchase_intent": prior_response.purchase_intent,
            "reasons": prior_response.reasons,
            "objections": prior_response.objections,
            "price_reaction": prior_response.price_reaction.model_dump(mode="json"),
            "preferred_channel": prior_response.preferred_channel,
            "uncertainty": prior_response.uncertainty,
            "confidence": prior_response.confidence,
            "citations": [citation.model_dump(mode="json") for citation in prior_response.citations],
            "grounding_refs": prior_response.grounding_refs,
            "explanation_trace": [step.model_dump(mode="json") for step in prior_response.explanation_trace],
            "follow_up_summary": (
                f"The agent highlights {', '.join(prior_response.reasons[:2]) or 'general interest'} "
                f"but remains cautious about {', '.join(prior_response.objections[:2]) or 'follow-up uncertainty'}."
            ),
        }
        if provider_name == "local"
        else None
    )
    request = build_chat_request(
        agent=agent,
        scenario=scenario,
        prompt_spec=prompt_spec,
        grounding_context=grounding_context,
        model_name=provider_model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        structured_response=structured_response,
        follow_up_context=follow_up_context,
    )
    response = provider_stack.chat.complete(request)
    if provider_name == "local":
        parsed = parse_agent_response_text(
            response_text=response.output_text,
            response_id=f"resp-{uuid.uuid4().hex[:8]}",
            scenario_id=scenario.scenario_id,
            agent_id=agent.agent_id,
            metadata=AgentResponseMetadata(
                provider_name=response.provider,
                provider_model=response.model,
                prompt_spec_id=prompt_spec.prompt_spec_id,
                attempt_count=1,
                mode=prompt_spec.mode,
                generated_at=datetime.now(timezone.utc),
            ),
        )
        return parsed.follow_up_summary or ""
    return response.output_text.strip()


def _build_local_structured_response(
    *,
    agent: SyntheticConsumerAgent,
    scenario: ScenarioDefinition,
    grounding_context: GroundingContext,
    mode: str,
) -> dict:
    price_options = [float(value) for value in scenario.product_or_service.price_options]
    max_price = max(price_options)
    purchase_intent = 3

    reasons: list[str] = []
    objections: list[str] = []
    explanation_trace: list[dict] = []

    if scenario.category[-1] in agent.category_preferences or "frozen_food" in agent.category_preferences:
        purchase_intent += 1
        reasons.append("カテゴリ適合性が高い")
        explanation_trace.append(
            {"step_id": "e-001", "kind": "evidence", "statement": "agent preferences include the scenario category", "confidence": "medium"}
        )

    if agent.convenience_orientation == "high":
        purchase_intent += 1
        reasons.append("時短メリットがある")

    if agent.health_orientation in {"medium", "high"}:
        reasons.append("健康訴求に反応しやすい")

    if agent.price_sensitivity == "high" and max_price >= 498:
        purchase_intent -= 1
        objections.append("価格が高い")

    if agent.household_composition == "family_with_children":
        objections.append("家族向けの量やコスパが気になる")

    if grounding_context.overall_uncertainty == "high":
        objections.append("根拠情報が十分ではない")
        purchase_intent = min(purchase_intent, 3)

    purchase_intent = max(1, min(5, purchase_intent))

    acceptable_price = 398.0 if agent.price_sensitivity == "high" else 498.0
    if agent.price_sensitivity == "low":
        acceptable_price = 598.0

    price_reaction = {
        str(int(price)): (
            "positive"
            if price <= acceptable_price
            else "cautious" if price <= acceptable_price + 100 else "negative"
        )
        for price in price_options
    }

    citations = [chunk.citation_trace.model_dump(mode="json") for chunk in grounding_context.chunks[:3]]
    grounding_refs = [chunk.citation_trace.trace_id for chunk in grounding_context.chunks[:3]]
    uncertainty = grounding_context.overall_uncertainty
    confidence = "low" if uncertainty == "high" else "medium" if uncertainty == "medium" else "high"

    if mode == "interview_multi_turn":
        explanation_trace.append(
            {"step_id": "e-002", "kind": "aggregation", "statement": "multi-turn follow-up requested", "confidence": "medium"}
        )

    return {
        "purchase_intent": purchase_intent,
        "reasons": list(dict.fromkeys(reasons)) or ["大きな強みはまだ限定的"],
        "objections": list(dict.fromkeys(objections)),
        "price_reaction": {
            "acceptable_price": acceptable_price,
            "reaction_by_price_option": price_reaction,
        },
        "preferred_channel": agent.channel_preference,
        "uncertainty": uncertainty,
        "confidence": confidence,
        "citations": citations,
        "grounding_refs": grounding_refs,
        "explanation_trace": explanation_trace,
        "follow_up_summary": None,
    }