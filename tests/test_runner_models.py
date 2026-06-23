from datetime import datetime, timezone

from requirement_insight_agent.core.config import ResolvedProviderConfig
from requirement_insight_agent.core.providers.local import LocalPlaceholderProvider
from requirement_insight_agent.core.providers.models import ChatMessage, ChatRequest
from simulations.models import (
    AgentResponseMetadata,
    AgentResponseRecord,
    ExplanationTraceStep,
    PriceReaction,
    PromptQuestionSpec,
    PromptSpec,
    PromptSpecMetadata,
)


def test_prompt_spec_requires_questions_and_instructions() -> None:
    spec = PromptSpec(
        prompt_spec_id="survey-v1",
        mode="survey",
        instructions=["JSON 形式で返答してください。"],
        questions=[
            PromptQuestionSpec(
                question_id="q1",
                text="この商品を試してみたいですか？",
                type="likert",
                required=True,
            )
        ],
        output_schema_hint={"purchase_intent": "1-5"},
        metadata=PromptSpecMetadata(version="0.1"),
    )

    assert spec.prompt_spec_id == "survey-v1"


def test_local_provider_returns_structured_json_when_requested() -> None:
    provider = LocalPlaceholderProvider(
        ResolvedProviderConfig(
            provider_name="local",
            chat_model="local-placeholder-chat",
            embedding_model="local-placeholder-embedding",
            response_prefix="[local]",
        )
    )

    response = provider.complete(
        ChatRequest(
            messages=[ChatMessage(role="user", content="Return JSON")],
            metadata={"structured_response": {"purchase_intent": 4, "reasons": ["便利"]}},
        )
    )

    assert '"purchase_intent": 4' in response.output_text


def test_agent_response_record_accepts_required_fields() -> None:
    record = AgentResponseRecord(
        response_id="resp-001",
        scenario_id="scenario-001",
        agent_id="agent-001",
        purchase_intent=4,
        reasons=["健康的", "時短"],
        objections=["価格が高い"],
        price_reaction=PriceReaction(acceptable_price=498, reaction_by_price_option={"398": "positive"}),
        preferred_channel="hybrid",
        uncertainty="medium",
        confidence="medium",
        citations=[],
        grounding_refs=[],
        explanation_trace=[
            ExplanationTraceStep(step_id="step-1", kind="evidence", statement="sample", confidence="medium")
        ],
        metadata=AgentResponseMetadata(
            provider_name="local",
            provider_model="local-placeholder-chat",
            prompt_spec_id="survey-v1",
            attempt_count=1,
            mode="survey",
            generated_at=datetime(2026, 6, 23, tzinfo=timezone.utc),
        ),
    )

    assert record.purchase_intent == 4