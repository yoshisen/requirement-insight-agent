"""Pydantic models for synthetic consumer agents.

These models implement the MVP-safe synthetic agent contract described in
docs/schema-spec.md. The schema avoids real-person identity fields and keeps the
representation distribution-oriented and auditable.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


ConfidenceLevel = Literal["low", "medium", "high"]
ChannelPreference = Literal["offline_first", "online_first", "hybrid"]
PriceSensitivity = Literal["low", "medium", "high"]


class UncertaintyProfile(BaseModel):
    """MVP uncertainty fields attached to each synthetic agent."""

    model_config = ConfigDict(extra="forbid")

    profile_confidence: ConfidenceLevel
    preference_uncertainty: ConfidenceLevel
    category_familiarity: ConfidenceLevel


class ResponseStyle(BaseModel):
    """Response behavior hints used by survey and interview runners."""

    model_config = ConfigDict(extra="forbid")

    verbosity: Literal["low", "medium", "high"]
    directness: Literal["low", "medium", "high"]
    confidence_expression: Literal["cautious", "balanced", "assertive"]


class AgentMetadata(BaseModel):
    """Generation metadata needed for reproducibility and auditability."""

    model_config = ConfigDict(extra="forbid")

    generated_at: datetime
    generator_version: str
    population_config_id: str
    seed: int | None = None
    synthetic_profile: bool = True
    notes: str | None = None

    @field_validator("synthetic_profile")
    @classmethod
    def validate_synthetic_profile(cls, value: bool) -> bool:
        if value is not True:
            raise ValueError("synthetic_profile must remain true for safety")
        return value


class AgentConstraints(BaseModel):
    """Practical constraints that shape purchasing behavior in simulation."""

    model_config = ConfigDict(extra="forbid")

    budget_constraints: str | None = None
    time_constraints: str | None = None
    storage_constraints: str | None = None
    access_constraints: str | None = None
    local_competition_context: str | None = None


class MemoryEntry(BaseModel):
    """Structured reasoning cue or prior note attached to a synthetic agent."""

    model_config = ConfigDict(extra="forbid")

    memory_id: str
    statement: str
    source: str | None = None
    confidence: ConfidenceLevel | None = None


class SyntheticConsumerAgent(BaseModel):
    """Population-aligned synthetic consumer representation for the MVP."""

    model_config = ConfigDict(extra="forbid")

    agent_id: str
    region: str
    catchment_area: str | None = None
    age_band: Literal["20s", "30s", "40s", "50s", "60_plus"]
    household_composition: Literal[
        "single",
        "couple",
        "family_with_children",
        "elderly_household",
    ]
    life_stage: str | None = None
    income_band: Literal["low", "lower_middle", "middle", "upper_middle", "high"]
    occupation_style: str | None = None
    mobility_pattern: str | None = None
    channel_preference: ChannelPreference
    price_sensitivity: PriceSensitivity
    shopping_mission_types: list[str] = Field(default_factory=list)
    category_preferences: list[str]
    category_aversions: list[str] = Field(default_factory=list)
    brand_loyalty_tendency: ConfidenceLevel | None = None
    novelty_seeking: ConfidenceLevel | None = None
    basket_size_tendency: Literal["small", "medium", "large"] | None = None
    impulse_purchase_tendency: ConfidenceLevel | None = None
    planning_tendency: ConfidenceLevel | None = None
    digital_literacy: ConfidenceLevel | None = None
    health_orientation: ConfidenceLevel | None = None
    eco_orientation: ConfidenceLevel | None = None
    convenience_orientation: ConfidenceLevel | None = None
    risk_aversion: ConfidenceLevel | None = None
    constraints: AgentConstraints | None = None
    rationale_memory: list[MemoryEntry] = Field(default_factory=list)
    grounding_context_refs: list[str] = Field(default_factory=list)
    worldview_tags: list[str] = Field(default_factory=list)
    uncertainty_profile: UncertaintyProfile
    response_style: ResponseStyle
    metadata: AgentMetadata

    @field_validator("category_preferences")
    @classmethod
    def validate_category_preferences(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("category_preferences must contain at least one item")
        return value