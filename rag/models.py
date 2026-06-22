"""Pydantic models for retrieval, provenance, and grounding artifacts."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agents.models import ConfidenceLevel


class Provenance(BaseModel):
    """Minimal provenance details required for an ingested datasource."""

    model_config = ConfigDict(extra="forbid")

    collected_by: str
    collected_method: str
    notes: str | None = None


class DataSourceMetadata(BaseModel):
    """Datasource contract with explicit license and allowed-use controls."""

    model_config = ConfigDict(extra="forbid")

    datasource_id: str
    source_name: str
    source_type: str
    source_url: str | None = None
    license_type: str
    allowed_use: list[str]
    retrieved_at: datetime
    coverage_region: list[str]
    coverage_time: str | None = None
    language: str | None = None
    format: str | None = None
    quality_score: float = Field(ge=0.0, le=1.0)
    known_biases: list[str] = Field(default_factory=list)
    provenance: Provenance

    @field_validator("allowed_use", "coverage_region")
    @classmethod
    def validate_non_empty_lists(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("list field must contain at least one item")
        return value


class CitationSourceRef(BaseModel):
    """Reference to the stored data object that produced a retrieved chunk."""

    model_config = ConfigDict(extra="forbid")

    datasource_id: str
    document_id: str | None = None
    chunk_id: str | None = None


class CitationUsedIn(BaseModel):
    """Execution context in which a citation trace was consumed."""

    model_config = ConfigDict(extra="forbid")

    scenario_id: str
    agent_id: str | None = None
    response_id: str | None = None
    output_id: str | None = None


class CitationTraceMetadata(BaseModel):
    """Retrieval metadata needed to explain how evidence was selected."""

    model_config = ConfigDict(extra="forbid")

    retrieved_at: datetime
    retrieval_method: str
    region_filter: str | None = None
    category_filter: str | None = None


class CitationTrace(BaseModel):
    """Structured provenance and citation trace for grounded outputs."""

    model_config = ConfigDict(extra="forbid")

    trace_id: str
    source_ref: CitationSourceRef
    used_in: CitationUsedIn
    citation_text: str
    relevance_score: float | None = Field(default=None, ge=0.0, le=1.0)
    metadata: CitationTraceMetadata


class RetrievedChunk(BaseModel):
    """Retrieved chunk plus metadata for downstream grounding or reporting."""

    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    document_id: str
    datasource_id: str
    title: str
    source_type: str
    text: str
    region_tags: list[str] = Field(default_factory=list)
    category_tags: list[str] = Field(default_factory=list)
    score: float = Field(ge=0.0, le=1.0)
    citation_trace: CitationTrace


class GroundingContext(BaseModel):
    """Bundle of retrieved evidence passed to a synthetic agent execution step."""

    model_config = ConfigDict(extra="forbid")

    context_id: str
    scenario_id: str
    chunks: list[RetrievedChunk]
    overall_uncertainty: ConfidenceLevel
    notes: list[str] = Field(default_factory=list)
