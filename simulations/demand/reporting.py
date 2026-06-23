"""Serialization helpers for demand estimation outputs."""

from __future__ import annotations

from pathlib import Path

from simulations.models import DemandEstimationOutput


def save_demand_estimation_output(estimation: DemandEstimationOutput, output_path: Path) -> Path:
    """Persist a demand estimation JSON output file."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(estimation.model_dump_json(indent=2), encoding="utf-8")
    return output_path


def save_demand_estimation_bundle(
    estimation: DemandEstimationOutput,
    inventory_suggestion: dict[str, dict[str, float]],
    output_path: Path,
) -> Path:
    """Persist a machine-readable bundle containing estimation and inventory suggestion."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        __import__("json").dumps(
            {
                "estimation": estimation.model_dump(mode="json"),
                "inventory_suggestion": inventory_suggestion,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return output_path