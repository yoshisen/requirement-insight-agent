"""Evaluation metrics for population representativeness and output stability."""

from __future__ import annotations

from collections import Counter
from math import fsum

from agents.population import PopulationBuildResult
from simulations.models import AggregatedOutput


def summarize_agent_distribution(population: PopulationBuildResult) -> dict[str, dict[str, float]]:
    """Summarize key population dimensions into comparable distributions."""

    records = population.records
    total = len(records) or 1

    return {
        "region": _distribution(Counter(record.agent.region for record in records), total),
        "age_band": _distribution(Counter(record.agent.age_band for record in records), total),
        "household_composition": _distribution(
            Counter(record.agent.household_composition for record in records), total
        ),
        "income_band": _distribution(Counter(record.agent.income_band for record in records), total),
        "channel_preference": _distribution(
            Counter(record.agent.channel_preference for record in records), total
        ),
        "price_sensitivity": _distribution(
            Counter(record.agent.price_sensitivity for record in records), total
        ),
    }


def representativeness_score(
    actual: dict[str, dict[str, float]],
    expected: dict[str, dict[str, float]],
) -> tuple[float, dict[str, float], list[str]]:
    """Compare actual and expected distributions with a simple bounded score."""

    dimension_scores: dict[str, float] = {}
    uncalibrated_areas: list[str] = []

    for dimension, expected_dist in expected.items():
        actual_dist = actual.get(dimension, {})
        keys = set(actual_dist) | set(expected_dist)
        distance = sum(abs(actual_dist.get(key, 0.0) - expected_dist.get(key, 0.0)) for key in keys) / 2
        score = max(0.0, 1.0 - distance)
        dimension_scores[dimension] = round(score, 4)
        if score < 0.8:
            uncalibrated_areas.append(dimension)

    overall = round(fsum(dimension_scores.values()) / max(len(dimension_scores), 1), 4)
    return overall, dimension_scores, uncalibrated_areas


def stability_score(reference: AggregatedOutput, candidate: AggregatedOutput | None = None) -> tuple[float, dict[str, float]]:
    """Compute a simple run-to-run stability score from aggregated outputs."""

    if candidate is None:
        candidate = reference

    ref_mean = reference.metrics.mean_purchase_intent or 0.0
    cand_mean = candidate.metrics.mean_purchase_intent or 0.0
    ref_ratio = reference.metrics.high_interest_ratio or 0.0
    cand_ratio = candidate.metrics.high_interest_ratio or 0.0
    mean_gap = abs(ref_mean - cand_mean) / 5.0
    ratio_gap = abs(ref_ratio - cand_ratio)
    overlap = reason_overlap(reference.summary.top_reasons, candidate.summary.top_reasons)
    score = max(0.0, 1.0 - ((mean_gap + ratio_gap) / 2) * 0.7 - (1.0 - overlap) * 0.3)
    detail = {
        "mean_purchase_intent_gap": round(mean_gap, 4),
        "high_interest_ratio_gap": round(ratio_gap, 4),
        "top_reason_overlap": round(overlap, 4),
    }
    return round(score, 4), detail


def evidence_coverage_score(aggregated: AggregatedOutput) -> float:
    """Estimate evidence coverage from citations and low-evidence flags."""

    citation_factor = min(1.0, len(aggregated.citation_summary) / 5.0)
    low_evidence_penalty = min(0.5, len(aggregated.uncertainty_summary.low_evidence_areas) * 0.1)
    return round(max(0.0, citation_factor - low_evidence_penalty), 4)


def bias_risk_level(aggregated: AggregatedOutput) -> str:
    """Map disagreement and uncertainty to a coarse bias-risk indicator."""

    disagreement = float(getattr(aggregated.metrics, "disagreement_score", 0.0) or 0.0)
    uncertainty = aggregated.uncertainty_summary.overall_uncertainty

    if uncertainty == "high" or disagreement >= 0.9:
        return "high"
    if uncertainty == "medium" or disagreement >= 0.45:
        return "medium"
    return "low"


def reason_overlap(left: list[str], right: list[str]) -> float:
    """Compute overlap ratio between top-reason sets."""

    left_set = set(left)
    right_set = set(right)
    if not left_set and not right_set:
        return 1.0
    if not left_set or not right_set:
        return 0.0
    return len(left_set & right_set) / len(left_set | right_set)


def _distribution(counts: Counter, total: int) -> dict[str, float]:
    return {key: count / total for key, count in counts.items()}