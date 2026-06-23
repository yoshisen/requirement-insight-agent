"""Scenario-based demand estimation heuristics.

This module intentionally produces bounded ranges and warnings rather than
single-point forecasts. It is a scenario estimator, not a forecasting engine.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field

from simulations.models import (
    AggregatedOutput,
    DemandEstimationInputRef,
    DemandEstimationMetadata,
    DemandEstimationOutput,
    DemandRange,
    SegmentSensitivity,
)


class DemandEstimationInput(BaseModel):
    """Normalized demand estimation input derived from aggregated outputs."""

    model_config = ConfigDict(extra="forbid")

    aggregation_output: AggregatedOutput
    base_units_per_period: int = Field(default=1000, ge=1)
    scenario_label: str = "base"


def build_demand_estimation(input_data: DemandEstimationInput) -> DemandEstimationOutput:
    """Estimate conservative, base, and optimistic demand ranges from aggregate signals."""

    aggregated = input_data.aggregation_output
    metrics = aggregated.metrics
    mean_intent = metrics.mean_purchase_intent or 0.0
    interest_ratio = metrics.high_interest_ratio or 0.0
    disagreement = float(getattr(metrics, "disagreement_score", 0.0) or 0.0)

    base_center = input_data.base_units_per_period * _interest_multiplier(mean_intent, interest_ratio)
    uncertainty_penalty = _uncertainty_penalty(aggregated.uncertainty_summary.overall_uncertainty, disagreement)
    conservative_center = base_center * (0.72 - uncertainty_penalty)
    optimistic_center = base_center * (1.22 - uncertainty_penalty / 2)

    segment_sensitivity = _build_segment_sensitivity(aggregated)
    assumptions = _build_assumptions(input_data)
    risk_factors = _build_risk_factors(aggregated)
    confidence = _map_confidence(aggregated.uncertainty_summary.overall_uncertainty, disagreement)
    warnings = _build_warnings(aggregated, confidence)

    return DemandEstimationOutput(
        estimation_id=f"demand-{uuid.uuid4().hex[:8]}",
        input_ref=DemandEstimationInputRef(
            aggregation_id=aggregated.output_id,
            population_id=aggregated.population_id,
        ),
        ranges={
            "conservative": _make_range(conservative_center, width_ratio=0.16),
            "base": _make_range(base_center, width_ratio=0.18),
            "optimistic": _make_range(optimistic_center, width_ratio=0.2),
        },
        assumptions=assumptions,
        risk_factors=risk_factors,
        segment_sensitivity=segment_sensitivity,
        confidence=confidence,
        warnings=warnings,
        metadata=DemandEstimationMetadata(generated_at=datetime.now(timezone.utc)),
    )


def _interest_multiplier(mean_intent: float, interest_ratio: float) -> float:
    intent_factor = 0.55 + (mean_intent / 5.0) * 0.75
    ratio_factor = 0.75 + interest_ratio * 0.5
    return intent_factor * ratio_factor


def _uncertainty_penalty(overall_uncertainty: str, disagreement: float) -> float:
    base_penalty = {"low": 0.02, "medium": 0.08, "high": 0.16}[overall_uncertainty]
    variance_penalty = min(0.1, disagreement * 0.08)
    return base_penalty + variance_penalty


def _make_range(center: float, width_ratio: float) -> DemandRange:
    lower = max(0.0, round(center * (1 - width_ratio), 2))
    upper = max(lower, round(center * (1 + width_ratio), 2))
    return DemandRange(lower=lower, upper=upper, unit="units_per_period")


def _build_assumptions(input_data: DemandEstimationInput) -> list[str]:
    aggregated = input_data.aggregation_output
    assumptions = [
        f"Estimation baseline uses {input_data.base_units_per_period} units_per_period as a scenario anchor.",
        f"Scenario label: {input_data.scenario_label}.",
        f"Mean purchase intent is interpreted from simulated agent responses: {aggregated.metrics.mean_purchase_intent or 0.0:.2f}.",
    ]
    if aggregated.metrics.high_interest_ratio is not None:
        assumptions.append(
            f"High-interest ratio contributes to upside range expansion: {aggregated.metrics.high_interest_ratio:.2%}."
        )
    return assumptions


def _build_risk_factors(aggregated: AggregatedOutput) -> list[str]:
    factors = []
    if aggregated.summary.top_objections:
        factors.append(f"Top objections remain active: {', '.join(aggregated.summary.top_objections[:2])}.")
    if aggregated.uncertainty_summary.high_disagreement_segments:
        factors.append(
            "Some segments show disagreement: "
            + ", ".join(aggregated.uncertainty_summary.high_disagreement_segments[:3])
            + "."
        )
    if aggregated.uncertainty_summary.low_evidence_areas:
        factors.append(
            "Evidence coverage is limited for: "
            + ", ".join(aggregated.uncertainty_summary.low_evidence_areas[:3])
            + "."
        )
    if not factors:
        factors.append("This estimate is still scenario-based and should be validated against real-world signals.")
    return factors


def _build_segment_sensitivity(aggregated: AggregatedOutput) -> list[SegmentSensitivity]:
    result: list[SegmentSensitivity] = []
    for segment in aggregated.segment_summaries:
        top_objection = segment.top_objections[0] if segment.top_objections else "major objections are limited"
        top_reason = segment.top_reasons[0] if segment.top_reasons else "clear reasons are limited"
        result.append(
            SegmentSensitivity(
                segment_key=segment.segment_key,
                note=f"{segment.segment_label}: key support is {top_reason}; key caution is {top_objection}.",
            )
        )
    return result


def _map_confidence(overall_uncertainty: str, disagreement: float) -> str:
    if overall_uncertainty == "high" or disagreement >= 0.9:
        return "low"
    if overall_uncertainty == "medium" or disagreement >= 0.45:
        return "medium"
    return "high"


def _build_warnings(aggregated: AggregatedOutput, confidence: str) -> list[str]:
    warnings = [
        "This output is a scenario-based estimate, not a deterministic forecast.",
    ]
    if confidence == "low":
        warnings.append("Low confidence warning: calibration is insufficient for strong operational commitments.")
    if aggregated.uncertainty_summary.overall_uncertainty != "low":
        warnings.append(
            f"Overall uncertainty is {aggregated.uncertainty_summary.overall_uncertainty}; validate against real-world data before operational use."
        )
    return warnings