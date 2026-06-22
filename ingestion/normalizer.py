"""Normalization helpers for ingestion outputs."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from rag.models import DataSourceMetadata

from .models import NormalizedDocument


def infer_document_kind(source_type: str) -> str:
    if source_type == "geospatial":
        return "region_info"
    if source_type == "product_catalog":
        return "product_info"
    if source_type in {"market_notes", "survey_results"}:
        return "market_note"
    return "generic_note"


def build_document_id(datasource_id: str, source_path: Path) -> str:
    stem = source_path.stem.replace("_", "-")
    return f"{datasource_id}::{stem}"


def normalize_document(
    *,
    datasource: DataSourceMetadata,
    source_path: Path,
    source_format: str,
    content: str,
) -> NormalizedDocument:
    title = source_path.stem.replace("_", " ").replace("-", " ").strip().title()
    return NormalizedDocument(
        document_id=build_document_id(datasource.datasource_id, source_path),
        datasource_id=datasource.datasource_id,
        source_path=str(source_path),
        source_format=source_format,
        document_kind=infer_document_kind(datasource.source_type),
        title=title or datasource.source_name,
        content=content,
        region_tags=datasource.coverage_region,
        category_tags=[datasource.source_type],
        quality_score=datasource.quality_score,
        created_at=datetime.now(timezone.utc),
        metadata={
            "license_type": datasource.license_type,
            "allowed_use": datasource.allowed_use,
            "source_name": datasource.source_name,
        },
    )