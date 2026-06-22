"""Models for datasource ingestion and normalized record output.

The ingestion layer reads local CSV / JSON / Markdown / text files together with
datasource metadata, then emits provenance-aware normalized records that later
RAG and scenario execution layers can consume.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from rag.models import DataSourceMetadata


LoaderHint = Literal["csv", "json", "markdown", "text"]
NormalizedContentFormat = Literal["csv_row", "json_item", "json_object", "markdown", "text"]


class IngestionSourceSpec(BaseModel):
    """Manifest entry describing one local source file plus its metadata."""

    model_config = ConfigDict(extra="forbid")

    source_path: str
    metadata: DataSourceMetadata
    loader_hint: LoaderHint | None = None
    title_field: str | None = None
    text_fields: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class LoadedRecord(BaseModel):
    """Intermediate loaded document or row before final normalization."""

    model_config = ConfigDict(extra="forbid")

    local_id: str
    content_format: NormalizedContentFormat
    title: str
    text: str
    structured_data: dict[str, Any] | None = None


class NormalizedRecord(BaseModel):
    """Normalized provenance-aware record written to data/processed/."""

    model_config = ConfigDict(extra="forbid")

    record_id: str
    datasource_id: str
    source_name: str
    source_type: str
    source_path: str
    content_format: NormalizedContentFormat
    title: str
    text: str
    structured_data: dict[str, Any] | None = None
    coverage_region: list[str]
    coverage_time: str | None = None
    language: str | None = None
    license_type: str
    allowed_use: list[str]
    quality_score: float = Field(ge=0.0, le=1.0)
    known_biases: list[str] = Field(default_factory=list)
    provenance: dict[str, Any]
    tags: list[str] = Field(default_factory=list)
    normalized_at: datetime

    @field_validator("coverage_region", "allowed_use")
    @classmethod
    def validate_non_empty_lists(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("list field must contain at least one item")
        return value


class IngestionResult(BaseModel):
    """Top-level result bundle produced by one ingestion run."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    created_at: datetime
    manifest_path: str
    source_count: int
    record_count: int
    records: list[NormalizedRecord]