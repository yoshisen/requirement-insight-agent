"""Synthetic population builder for the MVP.

This builder samples raw traits from weighted distributions, derives additional
traits plus rationale memory, and produces valid SyntheticConsumerAgent objects.
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path

from agents.memory import build_initial_explanation_trace
from agents.models import (
    AgentConstraints,
    AgentMetadata,
    ResponseStyle,
    SyntheticConsumerAgent,
    UncertaintyProfile,
)
from agents.population import (
    DerivedTraitProfile,
    GeneratedAgentRecord,
    PopulationBuildResult,
    PopulationConfig,
    RawTraitProfile,
    WeightedOption,
)


def load_population_config(path: Path) -> PopulationConfig:
    """Load a population config from JSON."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    return PopulationConfig.model_validate(payload)


def build_population(
    config: PopulationConfig,
    *,
    sample_size: int | None = None,
    category: str | None = None,
) -> PopulationBuildResult:
    """Generate a synthetic population aligned to the provided weighted config."""

    requested_size = sample_size or config.default_sample_size
    requested_category = category or config.default_category
    rng = random.Random(config.seed)
    records: list[GeneratedAgentRecord] = []
    conditioning = config.category_conditioning.get(requested_category)

    for index in range(requested_size):
        raw_traits = RawTraitProfile(
            region=_sample_weighted(config.region_weights, rng),
            age_band=_sample_weighted(config.age_band_weights, rng),
            household_composition=_sample_weighted(config.household_composition_weights, rng),
            income_band=_sample_weighted(config.income_band_weights, rng),
            channel_preference=_sample_weighted(
                _apply_boosts(config.channel_preference_weights, conditioning.channel_preference_boosts if conditioning else {}),
                rng,
            ),
            price_sensitivity=_sample_weighted(
                _apply_boosts(config.price_sensitivity_weights, conditioning.price_sensitivity_boosts if conditioning else {}),
                rng,
            ),
            requested_category=requested_category,
        )

        derived_traits = _derive_traits(raw_traits, conditioning)
        explanation_trace = build_initial_explanation_trace(
            [
                (f"mem-{index:04d}-raw", f"Raw traits sampled from weighted config for {raw_traits.age_band} / {raw_traits.household_composition}", "population_config", "high"),
                (f"mem-{index:04d}-category", f"Category conditioning applied for {requested_category}", "category_conditioning", "medium"),
                (f"mem-{index:04d}-derived", f"Derived traits emphasize {', '.join(derived_traits.category_preferences[:2])}", "trait_derivation", "medium"),
            ]
        )

        agent = SyntheticConsumerAgent(
            agent_id=f"tokyo-agent-{index + 1:04d}",
            region=raw_traits.region,
            age_band=raw_traits.age_band,
            household_composition=raw_traits.household_composition,
            income_band=raw_traits.income_band,
            life_stage=derived_traits.life_stage,
            occupation_style=derived_traits.occupation_style,
            mobility_pattern=derived_traits.mobility_pattern,
            channel_preference=raw_traits.channel_preference,
            price_sensitivity=raw_traits.price_sensitivity,
            shopping_mission_types=derived_traits.shopping_mission_types,
            category_preferences=derived_traits.category_preferences,
            convenience_orientation=derived_traits.convenience_orientation,
            health_orientation=derived_traits.health_orientation,
            eco_orientation=derived_traits.eco_orientation,
            risk_aversion=derived_traits.risk_aversion,
            digital_literacy=derived_traits.digital_literacy,
            worldview_tags=derived_traits.worldview_tags,
            constraints=_derive_constraints(raw_traits),
            rationale_memory=explanation_trace,
            grounding_context_refs=[],
            uncertainty_profile=_derive_uncertainty_profile(raw_traits),
            response_style=_derive_response_style(raw_traits),
            metadata=AgentMetadata(
                generated_at=datetime.now(timezone.utc),
                generator_version="0.1.0",
                population_config_id=config.population_config_id,
                seed=config.seed,
                notes=f"category={requested_category}",
            ),
        )

        records.append(
            GeneratedAgentRecord(
                record_id=f"{config.population_config_id}-{index + 1:04d}",
                agent=agent,
                raw_traits=raw_traits,
                derived_traits=derived_traits,
                explanation_trace=[entry.model_dump(mode="json") for entry in explanation_trace],
            )
        )

    return PopulationBuildResult(
        population_id=config.population_config_id,
        generated_at=datetime.now(timezone.utc),
        sample_size=requested_size,
        category=requested_category,
        seed=config.seed,
        records=records,
    )


def save_population_result(result: PopulationBuildResult, output_path: Path) -> Path:
    """Write generated synthetic population output to JSON."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return output_path


def _sample_weighted(options: list[WeightedOption], rng: random.Random) -> str:
    total = sum(option.weight for option in options)
    pick = rng.uniform(0, total)
    cumulative = 0.0
    for option in options:
        cumulative += option.weight
        if pick <= cumulative:
            return option.value
    return options[-1].value


def _apply_boosts(options: list[WeightedOption], boosts: dict[str, float]) -> list[WeightedOption]:
    boosted: list[WeightedOption] = []
    for option in options:
        boosted.append(
            WeightedOption(
                value=option.value,
                weight=max(0.001, option.weight + boosts.get(option.value, 0.0)),
            )
        )
    return boosted


def _derive_traits(raw_traits: RawTraitProfile, conditioning) -> DerivedTraitProfile:
    life_stage = _derive_life_stage(raw_traits.age_band, raw_traits.household_composition)
    occupation_style = _derive_occupation_style(raw_traits.age_band, raw_traits.household_composition)
    mobility_pattern = _derive_mobility(raw_traits.region, raw_traits.household_composition)
    shopping_mission_types = _derive_missions(raw_traits.household_composition)

    base_preferences = [raw_traits.requested_category]
    if conditioning:
        base_preferences.extend(conditioning.base_preferences)
        base_preferences.extend(conditioning.extra_preferences)

    deduped_preferences = list(dict.fromkeys(base_preferences))
    orientation_bias = conditioning.orientation_bias if conditioning else {}
    worldview_tags = list(dict.fromkeys((conditioning.worldview_tags if conditioning else []) + [raw_traits.requested_category]))

    return DerivedTraitProfile(
        life_stage=life_stage,
        occupation_style=occupation_style,
        mobility_pattern=mobility_pattern,
        shopping_mission_types=shopping_mission_types,
        category_preferences=deduped_preferences,
        convenience_orientation=orientation_bias.get("convenience_orientation", "medium"),
        health_orientation=orientation_bias.get("health_orientation", "medium"),
        eco_orientation=orientation_bias.get("eco_orientation", "low"),
        risk_aversion=_derive_risk_aversion(raw_traits.age_band),
        digital_literacy=_derive_digital_literacy(raw_traits.age_band),
        worldview_tags=worldview_tags,
    )


def _derive_life_stage(age_band: str, household: str) -> str | None:
    if age_band == "20s":
        return "early_career"
    if age_band == "30s" and household == "family_with_children":
        return "child_raising"
    if age_band == "60_plus":
        return "post_retirement"
    return None


def _derive_occupation_style(age_band: str, household: str) -> str | None:
    if age_band == "60_plus":
        return "retired"
    if household == "family_with_children":
        return "office_worker"
    return "office_worker"


def _derive_mobility(region: str, household: str) -> str | None:
    if "suburban" in region and household == "family_with_children":
        return "hybrid"
    return "public_transport"


def _derive_missions(household: str) -> list[str]:
    if household == "family_with_children":
        return ["planned_purchase", "bulk_buying"]
    if household == "single":
        return ["daily_restock", "planned_purchase"]
    return ["planned_purchase"]


def _derive_constraints(raw_traits: RawTraitProfile) -> AgentConstraints:
    return AgentConstraints(
        budget_constraints="moderate" if raw_traits.price_sensitivity != "low" else "relaxed",
        time_constraints="high" if raw_traits.household_composition in {"single", "family_with_children"} else "medium",
        storage_constraints="limited" if raw_traits.household_composition == "single" else "moderate",
        access_constraints="rail_access",
        local_competition_context=raw_traits.region,
    )


def _derive_uncertainty_profile(raw_traits: RawTraitProfile) -> UncertaintyProfile:
    familiarity = "high" if raw_traits.requested_category == "frozen_food" else "medium"
    preference_uncertainty = "high" if raw_traits.age_band == "20s" else "medium"
    return UncertaintyProfile(
        profile_confidence="medium",
        preference_uncertainty=preference_uncertainty,
        category_familiarity=familiarity,
    )


def _derive_response_style(raw_traits: RawTraitProfile) -> ResponseStyle:
    if raw_traits.household_composition == "single":
        return ResponseStyle(verbosity="medium", directness="high", confidence_expression="balanced")
    if raw_traits.household_composition == "elderly_household":
        return ResponseStyle(verbosity="medium", directness="medium", confidence_expression="cautious")
    return ResponseStyle(verbosity="medium", directness="medium", confidence_expression="balanced")


def _derive_risk_aversion(age_band: str) -> str:
    return "high" if age_band in {"50s", "60_plus"} else "medium"


def _derive_digital_literacy(age_band: str) -> str:
    return "high" if age_band in {"20s", "30s"} else "medium"