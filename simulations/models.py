"""Pydantic models for scenarios, aggregated outputs, and demand estimation."""

from __future__ import annotations

from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator, field_validator

from agents.models import ConfidenceLevel
from rag.models import CitationTrace


class ProductOrService(BaseModel):
    """Minimal product or service brief used in scenario execution."""

    model_config = ConfigDict(extra="forbid")

    name: str
    description: str
    price_options: list[float]
    positioning: str | list[str]

    @field_validator("price_options")
    @classmethod
    def validate_price_options(cls, value: list[float]) -> list[float]:
        if not value:
            raise ValueError("price_options must contain at least one value")
        return value


class TargetAgents(BaseModel):
    """Selection criteria for synthetic agents targeted by a scenario."""

    model_config = ConfigDict(extra="forbid")

    population_id: str
    selection_filters: dict[str, object] | list[str] = Field(default_factory=dict)
    sample_size: int = Field(ge=1)


class ScenarioVariant(BaseModel):
    """Optional variant definition for price, channel, or promotion changes."""

    model_config = ConfigDict(extra="forbid")

    variant_id: str
    label: str
    changes: dict[str, object]


class ScenarioMetadata(BaseModel):
    """Creation metadata for scenario definitions."""

    model_config = ConfigDict(extra="forbid")

    created_at: datetime
    created_by: str = Field(validation_alias=AliasChoices("created_by", "author"))
    version: str


class ScenarioDefinition(BaseModel):
    """Structured business scenario used by the MVP pipeline."""

    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    title: str
    region: list[str]
    category: list[str]
    business_question: str
    product_or_service: ProductOrService
    comparison_targets: list[str] = Field(default_factory=list)
    target_agents: TargetAgents
    evaluation_dimensions: list[str]
    assumptions: list[str]
    constraints: list[str] = Field(default_factory=list)
    scenario_variants: list[ScenarioVariant] = Field(default_factory=list)
    metadata: ScenarioMetadata

    @field_validator("region", "category", "evaluation_dimensions", "assumptions")
    @classmethod
    def validate_required_lists(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("list field must contain at least one item")
        return value


class PromptQuestionSpec(BaseModel):
    """One survey or interview question used by the orchestration layer."""

    model_config = ConfigDict(extra="forbid")

    question_id: str
    text: str
    type: str
    required: bool
    scale: dict[str, object] | None = None
    choices: list[str] | None = None


class PromptSpecMetadata(BaseModel):
    """Version and bookkeeping metadata for prompt specs."""

    model_config = ConfigDict(extra="allow")

    version: str


class PromptSpec(BaseModel):
    """Prompt specification used for survey and interview execution."""

    model_config = ConfigDict(extra="forbid")

    prompt_spec_id: str
    mode: str
    instructions: list[str]
    questions: list[PromptQuestionSpec]
    output_schema_hint: dict[str, object]
    metadata: PromptSpecMetadata

    @field_validator("instructions", "questions")
    @classmethod
    def validate_non_empty_lists(cls, value: list[object]) -> list[object]:
        if not value:
            raise ValueError("prompt spec lists must not be empty")
        return value


class PriceReaction(BaseModel):
    """Structured price reaction summary for one synthetic agent response."""

    model_config = ConfigDict(extra="forbid")

    acceptable_price: float | None = None
    reaction_by_price_option: dict[str, str] = Field(default_factory=dict)


class AgentResponseMetadata(BaseModel):
    """Execution metadata for one structured agent response."""

    model_config = ConfigDict(extra="forbid")

    provider_name: str
    provider_model: str
    prompt_spec_id: str
    attempt_count: int
    mode: str
    generated_at: datetime


class AgentResponseRecord(BaseModel):
    """Structured result returned by one survey or interview execution."""

    model_config = ConfigDict(extra="forbid")

    response_id: str
    scenario_id: str
    agent_id: str
    purchase_intent: int = Field(ge=1, le=5)
    reasons: list[str] = Field(default_factory=list)
    objections: list[str] = Field(default_factory=list)
    price_reaction: PriceReaction
    preferred_channel: str
    uncertainty: ConfidenceLevel
    confidence: ConfidenceLevel
    citations: list[CitationTrace] = Field(default_factory=list)
    grounding_refs: list[str] = Field(default_factory=list)
    explanation_trace: list[ExplanationTraceStep] = Field(default_factory=list)
    follow_up_summary: str | None = None
    metadata: AgentResponseMetadata


class ScenarioRunResult(BaseModel):
    """Serializable bundle for one scenario run over a set of synthetic agents."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    scenario_id: str
    prompt_spec_id: str
    mode: str
    response_count: int
    responses: list[AgentResponseRecord]
    metadata: dict[str, object] = Field(default_factory=dict)


class AggregationSummary(BaseModel):
    """Top-level summary extracted from aggregated agent responses."""

    model_config = ConfigDict(extra="forbid")

    overall_takeaway: str
    top_reasons: list[str] = Field(default_factory=list)
    top_objections: list[str] = Field(default_factory=list)


class SegmentSummary(BaseModel):
    """Segment-level summary for one slice of the synthetic population."""

    model_config = ConfigDict(extra="forbid")

    segment_key: str
    segment_label: str
    takeaway: str
    sample_size: int = Field(ge=0)
    purchase_intent_distribution: dict[str, float] = Field(default_factory=dict)
    top_reasons: list[str] = Field(default_factory=list)
    top_objections: list[str] = Field(default_factory=list)


class OutputMetrics(BaseModel):
    """Metrics emitted by deterministic aggregation logic."""

    model_config = ConfigDict(extra="allow")

    mean_purchase_intent: float | None = None
    high_interest_ratio: float | None = None
    price_sensitivity_summary: str | dict[str, object] | None = None
    channel_preference_summary: str | dict[str, object] | None = None


class UncertaintySummary(BaseModel):
    """Summary of disagreement and evidence limitations in one output."""

    model_config = ConfigDict(extra="forbid")

    overall_uncertainty: ConfidenceLevel
    high_disagreement_segments: list[str] = Field(default_factory=list)
    low_evidence_areas: list[str] = Field(default_factory=list)


class ExplanationTraceStep(BaseModel):
    """One structured reasoning step preserved for explainability."""

    model_config = ConfigDict(extra="forbid")

    step_id: str
    kind: str
    statement: str
    citation_trace_ids: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel | None = None


class DemandRange(BaseModel):
    """A numeric range with unit for scenario-based demand estimates."""

    model_config = ConfigDict(extra="forbid")

    lower: float
    upper: float
    unit: str

    @model_validator(mode="after")
    def validate_bounds(self) -> "DemandRange":
        if self.lower > self.upper:
            raise ValueError("range lower bound must be less than or equal to upper bound")
        return self


class DemandEstimationInputRef(BaseModel):
    """Reference back to the aggregated output that informed an estimate."""

    model_config = ConfigDict(extra="forbid")

    aggregation_id: str
    population_id: str


class SegmentSensitivity(BaseModel):
    """One segment-specific note about demand sensitivity."""

    model_config = ConfigDict(extra="forbid")

    segment_key: str
    note: str


class DemandEstimationMetadata(BaseModel):
    """Generation metadata for demand estimation outputs."""

    model_config = ConfigDict(extra="forbid")

    generated_at: datetime


class DemandEstimationOutput(BaseModel):
    """Scenario-based demand and inventory suggestion output."""

    model_config = ConfigDict(extra="forbid")

    estimation_id: str
    input_ref: DemandEstimationInputRef
    ranges: dict[str, DemandRange]
    assumptions: list[str]
    risk_factors: list[str] = Field(default_factory=list)
    segment_sensitivity: list[SegmentSensitivity] = Field(default_factory=list)
    confidence: ConfidenceLevel
    warnings: list[str] = Field(default_factory=list)
    metadata: DemandEstimationMetadata

    @field_validator("assumptions")
    @classmethod
    def validate_assumptions(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("assumptions must contain at least one item")
        return value

    @model_validator(mode="after")
    def validate_required_ranges(self) -> "DemandEstimationOutput":
        for key in ("conservative", "base", "optimistic"):
            if key not in self.ranges:
                raise ValueError(f"ranges must include '{key}'")
        return self


class OutputMetadata(BaseModel):
    """Metadata for aggregated outputs and bundled scenario results."""

    model_config = ConfigDict(extra="forbid")

    generated_at: datetime
    generator_version: str
    prompt_spec_id: str | None = None
    notes: str | None = None


class AggregatedOutput(BaseModel):
    """Structured aggregated output bundle for one scenario run."""

    model_config = ConfigDict(extra="forbid")

    output_id: str
    scenario_id: str
    population_id: str
    summary: AggregationSummary
    segment_summaries: list[SegmentSummary] = Field(default_factory=list)
    metrics: OutputMetrics
    uncertainty_summary: UncertaintySummary
    citation_summary: list[CitationTrace] = Field(default_factory=list)
    explanation_trace: list[ExplanationTraceStep] = Field(default_factory=list)
    demand_estimation: DemandEstimationOutput | None = None
    metadata: OutputMetadata
