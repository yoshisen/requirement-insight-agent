"""Population configuration and output models for synthetic agent generation.

The generation layer separates raw sampled traits from derived traits so future
calibration can reason about where each attribute came from.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agents.models import ConfidenceLevel, SyntheticConsumerAgent


class WeightedOption(BaseModel):
    """Weighted categorical option used for distribution-based sampling."""

    model_config = ConfigDict(extra="forbid")

    value: str
    weight: float = Field(gt=0)


class CategoryConditioning(BaseModel):
    """Category-specific adjustments applied on top of raw sampled traits."""

    model_config = ConfigDict(extra="forbid")

    base_preferences: list[str] = Field(default_factory=list)
    extra_preferences: list[str] = Field(default_factory=list)
    channel_preference_boosts: dict[str, float] = Field(default_factory=dict)
    price_sensitivity_boosts: dict[str, float] = Field(default_factory=dict)
    orientation_bias: dict[str, str] = Field(default_factory=dict)
    worldview_tags: list[str] = Field(default_factory=list)


class PopulationConfig(BaseModel):
    """Configurable distribution inputs for population-aligned agent generation."""

    model_config = ConfigDict(extra="forbid")

    population_config_id: str
    seed: int
    default_sample_size: int = Field(ge=1)
    default_region: str
    default_category: str
    region_weights: list[WeightedOption]
    age_band_weights: list[WeightedOption]
    household_composition_weights: list[WeightedOption]
    income_band_weights: list[WeightedOption]
    channel_preference_weights: list[WeightedOption]
    price_sensitivity_weights: list[WeightedOption]
    category_conditioning: dict[str, CategoryConditioning] = Field(default_factory=dict)

    @field_validator(
        "region_weights",
        "age_band_weights",
        "household_composition_weights",
        "income_band_weights",
        "channel_preference_weights",
        "price_sensitivity_weights",
    )
    @classmethod
    def validate_weight_lists(cls, value: list[WeightedOption]) -> list[WeightedOption]:
        if not value:
            raise ValueError("weight lists must contain at least one option")
        return value


class RawTraitProfile(BaseModel):
    """Directly sampled traits before derivation and category conditioning."""

    model_config = ConfigDict(extra="forbid")

    region: str
    age_band: str
    household_composition: str
    income_band: str
    channel_preference: str
    price_sensitivity: str
    requested_category: str


class DerivedTraitProfile(BaseModel):
    """Traits derived from raw traits plus category conditioning."""

    model_config = ConfigDict(extra="forbid")

    life_stage: str | None = None
    occupation_style: str | None = None
    mobility_pattern: str | None = None
    shopping_mission_types: list[str] = Field(default_factory=list)
    category_preferences: list[str] = Field(default_factory=list)
    convenience_orientation: ConfidenceLevel | None = None
    health_orientation: ConfidenceLevel | None = None
    eco_orientation: ConfidenceLevel | None = None
    risk_aversion: ConfidenceLevel | None = None
    digital_literacy: ConfidenceLevel | None = None
    worldview_tags: list[str] = Field(default_factory=list)


class GeneratedAgentRecord(BaseModel):
    """Generated synthetic agent with calibration-friendly trait provenance."""

    model_config = ConfigDict(extra="forbid")

    record_id: str
    agent: SyntheticConsumerAgent
    raw_traits: RawTraitProfile
    derived_traits: DerivedTraitProfile
    explanation_trace: list[dict] = Field(default_factory=list)


class PopulationBuildResult(BaseModel):
    """Serializable output bundle produced by one population build run."""

    model_config = ConfigDict(extra="forbid")

    population_id: str
    generated_at: datetime
    sample_size: int
    category: str
    seed: int
    records: list[GeneratedAgentRecord]