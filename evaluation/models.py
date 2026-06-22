"""Pydantic models for evaluation and calibration records."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agents.models import ConfidenceLevel
from rag.models import CitationTrace


class EvaluationMetrics(BaseModel):
    """Common evaluation metrics with room for future extension."""

    model_config = ConfigDict(extra="allow")

    representativeness_score: float | None = Field(default=None, ge=0.0, le=1.0)
    stability_score: float | None = Field(default=None, ge=0.0, le=1.0)
    evidence_coverage_score: float | None = Field(default=None, ge=0.0, le=1.0)
    bias_risk_level: ConfidenceLevel | None = None


class UncertaintyMonitoring(BaseModel):
    """Tracks disagreement and uncertainty signals during evaluation."""

    model_config = ConfigDict(extra="forbid")

    overall_uncertainty: ConfidenceLevel | None = None
    disagreement_signals: list[str] = Field(default_factory=list)


class EvaluationMetadata(BaseModel):
    """Metadata describing when and with which evaluator a record was created."""

    model_config = ConfigDict(extra="forbid")

    generated_at: datetime
    evaluator_version: str | None = None
    notes: str | None = None


class EvaluationRecord(BaseModel):
    """Evaluation or calibration result for a population or scenario artifact."""

    model_config = ConfigDict(extra="forbid")

    evaluation_id: str
    target_type: Literal["population", "scenario_run", "aggregation", "demand_estimation"]
    target_ref: dict[str, object]
    metrics: EvaluationMetrics
    findings: list[str]
    calibration_recommendations: list[str] = Field(default_factory=list)
    benchmark_refs: list[str] = Field(default_factory=list)
    uncalibrated_areas: list[str] = Field(default_factory=list)
    uncertainty_monitoring: UncertaintyMonitoring | None = None
    citation_summary: list[CitationTrace] = Field(default_factory=list)
    metadata: EvaluationMetadata

    @field_validator("findings")
    @classmethod
    def validate_findings(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("findings must contain at least one item")
        return value