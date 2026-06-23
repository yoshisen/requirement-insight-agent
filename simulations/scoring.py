"""Deterministic scoring helpers for aggregation and reporting."""

from __future__ import annotations

from collections import Counter, defaultdict
from math import sqrt

from agents.models import SyntheticConsumerAgent
from simulations.models import AgentResponseRecord


def mean_purchase_intent(responses: list[AgentResponseRecord]) -> float:
    if not responses:
        return 0.0
    return sum(response.purchase_intent for response in responses) / len(responses)


def high_interest_ratio(responses: list[AgentResponseRecord], threshold: int = 4) -> float:
    if not responses:
        return 0.0
    return sum(1 for response in responses if response.purchase_intent >= threshold) / len(responses)


def purchase_intent_distribution(responses: list[AgentResponseRecord]) -> dict[str, float]:
    if not responses:
        return {str(score): 0.0 for score in range(1, 6)}

    counts = Counter(response.purchase_intent for response in responses)
    total = len(responses)
    return {str(score): counts.get(score, 0) / total for score in range(1, 6)}


def top_terms(values: list[str], limit: int = 3) -> list[str]:
    normalized = [value.strip() for value in values if value.strip()]
    if not normalized:
        return []
    counts = Counter(normalized)
    return [item for item, _ in counts.most_common(limit)]


def channel_preference_summary(responses: list[AgentResponseRecord]) -> dict[str, float]:
    if not responses:
        return {}

    counts = Counter(response.preferred_channel for response in responses)
    total = len(responses)
    return {channel: count / total for channel, count in counts.items()}


def price_sensitivity_summary(
    responses: list[AgentResponseRecord],
    agent_lookup: dict[str, SyntheticConsumerAgent],
) -> dict[str, dict[str, float]]:
    grouped_scores: dict[str, list[float]] = defaultdict(list)
    grouped_prices: dict[str, list[float]] = defaultdict(list)

    for response in responses:
        agent = agent_lookup.get(response.agent_id)
        if agent is None:
            continue
        grouped_scores[agent.price_sensitivity].append(float(response.purchase_intent))
        if response.price_reaction.acceptable_price is not None:
            grouped_prices[agent.price_sensitivity].append(float(response.price_reaction.acceptable_price))

    summary: dict[str, dict[str, float]] = {}
    for bucket, scores in grouped_scores.items():
        summary[bucket] = {
            "sample_size": float(len(scores)),
            "mean_purchase_intent": sum(scores) / len(scores),
            "mean_acceptable_price": (
                sum(grouped_prices[bucket]) / len(grouped_prices[bucket]) if grouped_prices[bucket] else 0.0
            ),
        }
    return summary


def disagreement_score(responses: list[AgentResponseRecord]) -> float:
    if len(responses) <= 1:
        return 0.0
    mean_value = mean_purchase_intent(responses)
    variance = sum((response.purchase_intent - mean_value) ** 2 for response in responses) / len(responses)
    return sqrt(variance)