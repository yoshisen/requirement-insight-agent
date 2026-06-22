"""Chunk normalized ingestion records into retrieval-ready text units."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ingestion.models import NormalizedRecord as IngestedRecord


class ChunkingConfig(BaseModel):
    """Chunking parameters for the MVP retrieval corpus."""

    model_config = ConfigDict(extra="forbid")

    chunk_size: int = Field(default=220, ge=40)
    chunk_overlap: int = Field(default=40, ge=0)

    @field_validator("chunk_overlap")
    @classmethod
    def validate_overlap(cls, value: int, info):
        chunk_size = info.data.get("chunk_size", 220)
        if value >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        return value


class ChunkRecord(BaseModel):
    """One retrieval-ready chunk derived from a normalized ingestion record."""

    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    record_id: str
    datasource_id: str
    source_type: str
    title: str
    text: str
    chunk_index: int
    chunk_count: int
    region_tags: list[str] = Field(default_factory=list)
    category_tags: list[str] = Field(default_factory=list)
    quality_score: float = Field(ge=0.0, le=1.0)


def chunk_normalized_records(
    records: list[IngestedRecord],
    config: ChunkingConfig | None = None,
) -> list[ChunkRecord]:
    """Split normalized ingestion records into retrieval-ready chunks."""

    config = config or ChunkingConfig()
    chunks: list[ChunkRecord] = []

    for record in records:
        text_chunks = _split_text(record.text, config.chunk_size, config.chunk_overlap)
        chunk_count = len(text_chunks)

        for index, text in enumerate(text_chunks):
            chunks.append(
                ChunkRecord(
                    chunk_id=f"{record.record_id}::chunk-{index:03d}",
                    record_id=record.record_id,
                    datasource_id=record.datasource_id,
                    source_type=record.source_type,
                    title=record.title,
                    text=text,
                    chunk_index=index,
                    chunk_count=chunk_count,
                    region_tags=record.coverage_region,
                    category_tags=_derive_category_tags(record),
                    quality_score=record.quality_score,
                )
            )

    return chunks


def _split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    cleaned = " ".join(text.split())
    if len(cleaned) <= chunk_size:
        return [cleaned]

    step = chunk_size - chunk_overlap
    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = start + chunk_size
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(cleaned):
            break
        start += step
    return chunks


def _derive_category_tags(record: IngestedRecord) -> list[str]:
    tags = list(record.tags)
    if record.source_type not in tags:
        tags.append(record.source_type)
    if record.structured_data and isinstance(record.structured_data, dict):
        category = record.structured_data.get("category")
        if isinstance(category, str) and category not in tags:
            tags.append(category)
    lowered = record.text.lower()
    if "frozen" in lowered and "frozen_food" not in tags:
        tags.append("frozen_food")
    if "冷凍" in record.text and "frozen_food" not in tags:
        tags.append("frozen_food")
    return tags