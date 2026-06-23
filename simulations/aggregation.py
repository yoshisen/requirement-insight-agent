"""Deterministic aggregation of scenario run responses."""

from __future__ import annotations

import json
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from agents.models import SyntheticConsumerAgent
from agents.population import PopulationBuildResult
from rag.models import CitationTrace
from simulations.models import (
    AggregatedOutput,
    AggregationSummary,
    ExplanationTraceStep,
    OutputMetadata,
    OutputMetrics,
    ScenarioRunResult,
    SegmentSummary,
    UncertaintySummary,
)
from simulations.scoring import (
    channel_preference_summary,
    disagreement_score,
    high_interest_ratio,
    mean_purchase_intent,
    price_sensitivity_summary,
    purchase_intent_distribution,
    top_terms,
)


def load_run_result(path: Path) -> ScenarioRunResult:
    """Load a saved scenario run result JSON file."""

    return ScenarioRunResult.model_validate(json.loads(path.read_text(encoding="utf-8")))


def load_aggregated_output(path: Path) -> AggregatedOutput:
    """Load a saved aggregated output JSON file."""

    return AggregatedOutput.model_validate(json.loads(path.read_text(encoding="utf-8")))


def aggregate_run(
    *,
    run_result: ScenarioRunResult,
    population: PopulationBuildResult,
) -> AggregatedOutput:
    """Aggregate per-agent responses into a structured scenario output bundle."""

    responses = run_result.responses
    agent_lookup = {record.agent.agent_id: record.agent for record in population.records}

    summary = AggregationSummary(
        overall_takeaway=_build_overall_takeaway(responses),
        top_reasons=top_terms([reason for response in responses for reason in response.reasons]),
        top_objections=top_terms([objection for response in responses for objection in response.objections]),
    )

    segment_summaries = _build_segment_summaries(responses, agent_lookup)
    metrics = OutputMetrics(
        mean_purchase_intent=mean_purchase_intent(responses),
        high_interest_ratio=high_interest_ratio(responses),
        price_sensitivity_summary=price_sensitivity_summary(responses, agent_lookup),
        channel_preference_summary=channel_preference_summary(responses),
        disagreement_score=disagreement_score(responses),
        overall_purchase_intent_distribution=purchase_intent_distribution(responses),
    )
    uncertainty_summary = _build_uncertainty_summary(responses, segment_summaries)
    citation_summary = _dedupe_citations(responses)
    explanation_trace = _build_explanation_trace(responses, summary, uncertainty_summary)

    return AggregatedOutput(
        output_id=f"agg-{uuid.uuid4().hex[:8]}",
        scenario_id=run_result.scenario_id,
        population_id=population.population_id,
        summary=summary,
        segment_summaries=segment_summaries,
        metrics=metrics,
        uncertainty_summary=uncertainty_summary,
        citation_summary=citation_summary,
        explanation_trace=explanation_trace,
        metadata=OutputMetadata(
            generated_at=datetime.now(timezone.utc),
            generator_version="0.1.0",
            prompt_spec_id=run_result.prompt_spec_id,
            notes="This output is a structured hypothesis-support summary, not deterministic market truth.",
        ),
    )


def save_aggregated_output(output: AggregatedOutput, output_path: Path) -> Path:
    """Persist an aggregated output JSON file."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output.model_dump_json(indent=2), encoding="utf-8")
    return output_path


def _build_overall_takeaway(responses) -> str:
    mean_value = mean_purchase_intent(responses)
    reasons = top_terms([reason for response in responses for reason in response.reasons], limit=2)
    objections = top_terms([objection for response in responses for objection in response.objections], limit=2)

    if mean_value >= 4.0:
        tone = "関心は高め"
    elif mean_value >= 3.0:
        tone = "関心は中位"
    else:
        tone = "関心は限定的"

    reasons_text = "、".join(reasons) if reasons else "明確な支持理由は限定的"
    objections_text = "、".join(objections) if objections else "大きな反対理由は目立たない"
    return f"{tone}だが、主な支持理由は{reasons_text}、一方で{objections_text}に注意が必要。"


def _build_segment_summaries(responses, agent_lookup: dict[str, SyntheticConsumerAgent]) -> list[SegmentSummary]:
    grouped: dict[str, list] = defaultdict(list)
    labels: dict[str, str] = {}

    for response in responses:
        agent = agent_lookup.get(response.agent_id)
        if agent is None:
            continue
        segment_key = f"{agent.household_composition}__{agent.age_band}"
        labels[segment_key] = f"{agent.household_composition} / {agent.age_band}"
        grouped[segment_key].append(response)

    summaries: list[SegmentSummary] = []
    for segment_key, segment_responses in grouped.items():
        summaries.append(
            SegmentSummary(
                segment_key=segment_key,
                segment_label=labels[segment_key],
                takeaway=_build_overall_takeaway(segment_responses),
                sample_size=len(segment_responses),
                purchase_intent_distribution=purchase_intent_distribution(segment_responses),
                top_reasons=top_terms([reason for response in segment_responses for reason in response.reasons]),
                top_objections=top_terms([objection for response in segment_responses for objection in response.objections]),
            )
        )

    summaries.sort(key=lambda item: item.segment_key)
    return summaries


def _build_uncertainty_summary(responses, segment_summaries: list[SegmentSummary]) -> UncertaintySummary:
    uncertainty_levels = [response.uncertainty for response in responses]
    if "high" in uncertainty_levels:
        overall = "high"
    elif "medium" in uncertainty_levels:
        overall = "medium"
    else:
        overall = "low"

    high_disagreement_segments = [
        segment.segment_key
        for segment in segment_summaries
        if _distribution_spread(segment.purchase_intent_distribution) >= 0.45
    ]
    low_evidence_areas = [
        response.agent_id
        for response in responses
        if len(response.citations) < 2 or response.uncertainty == "high"
    ]

    return UncertaintySummary(
        overall_uncertainty=overall,
        high_disagreement_segments=high_disagreement_segments,
        low_evidence_areas=low_evidence_areas,
    )


def _distribution_spread(distribution: dict[str, float]) -> float:
    values = list(distribution.values())
    return max(values) - min(values) if values else 0.0


def _dedupe_citations(responses) -> list[CitationTrace]:
    seen: dict[str, CitationTrace] = {}
    for response in responses:
        for citation in response.citations:
            seen.setdefault(citation.trace_id, citation)
    return list(seen.values())


def _build_explanation_trace(
    responses,
    summary: AggregationSummary,
    uncertainty_summary: UncertaintySummary,
) -> list[ExplanationTraceStep]:
    trace: list[ExplanationTraceStep] = []

    for response in responses:
        for step in response.explanation_trace:
            trace.append(
                ExplanationTraceStep(
                    step_id=f"{response.agent_id}-{step.step_id}",
                    kind=step.kind,
                    statement=f"{response.agent_id}: {step.statement}",
                    citation_trace_ids=response.grounding_refs,
                    confidence=step.confidence,
                )
            )

    trace.append(
        ExplanationTraceStep(
            step_id="agg-summary",
            kind="aggregation",
            statement=summary.overall_takeaway,
            citation_trace_ids=[],
            confidence="medium",
        )
    )
    trace.append(
        ExplanationTraceStep(
            step_id="agg-uncertainty",
            kind="uncertainty",
            statement=(
                f"overall uncertainty is {uncertainty_summary.overall_uncertainty}; "
                f"high disagreement segments: {', '.join(uncertainty_summary.high_disagreement_segments) or 'none'}"
            ),
            citation_trace_ids=[],
            confidence=uncertainty_summary.overall_uncertainty,
        )
    )

    return trace