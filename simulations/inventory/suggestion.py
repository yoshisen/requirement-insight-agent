"""Inventory suggestion helpers derived from demand estimation ranges."""

from __future__ import annotations

from simulations.models import DemandEstimationOutput


def build_inventory_suggestion(estimation: DemandEstimationOutput) -> dict[str, dict[str, float]]:
    """Return inventory suggestion ranges derived from demand estimation output."""

    return {
        scenario: {
            "suggested_min_stock": round(range_output.lower * 0.9, 2),
            "suggested_max_stock": round(range_output.upper * 1.05, 2),
        }
        for scenario, range_output in estimation.ranges.items()
    }