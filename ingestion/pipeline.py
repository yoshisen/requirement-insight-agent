"""Ingestion pipeline for local datasource manifests and normalization."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from ingestion.loaders import load_records
from ingestion.models import IngestionResult, IngestionSourceSpec, NormalizedRecord


def load_manifest(manifest_path: Path) -> list[IngestionSourceSpec]:
    """Load and validate the datasource manifest."""

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("manifest must be a list of ingestion source specs")

    return [IngestionSourceSpec.model_validate(item) for item in payload]


def ingest_from_manifest(manifest_path: Path, source_root: Path | None = None) -> IngestionResult:
    """Load a datasource manifest and normalize all listed sources."""

    manifest_path = manifest_path.resolve()
    source_root = (source_root or manifest_path.parent).resolve()
    specs = load_manifest(manifest_path)
    created_at = datetime.now(timezone.utc)
    records: list[NormalizedRecord] = []

    for spec in specs:
        source_path = (source_root / spec.source_path).resolve()
        loaded_records = load_records(spec, source_path)

        for index, loaded in enumerate(loaded_records):
            records.append(
                NormalizedRecord(
                    record_id=f"{spec.metadata.datasource_id}-{index:04d}",
                    datasource_id=spec.metadata.datasource_id,
                    source_name=spec.metadata.source_name,
                    source_type=spec.metadata.source_type,
                    source_path=str(source_path.relative_to(source_root.parent))
                    if source_root.parent in source_path.parents or source_path.parent == source_root.parent
                    else str(source_path),
                    content_format=loaded.content_format,
                    title=loaded.title,
                    text=loaded.text,
                    structured_data=loaded.structured_data,
                    coverage_region=spec.metadata.coverage_region,
                    coverage_time=spec.metadata.coverage_time,
                    language=spec.metadata.language,
                    license_type=spec.metadata.license_type,
                    allowed_use=spec.metadata.allowed_use,
                    quality_score=spec.metadata.quality_score,
                    known_biases=spec.metadata.known_biases,
                    provenance=spec.metadata.provenance.model_dump(mode="json"),
                    tags=spec.tags,
                    normalized_at=created_at,
                )
            )

    return IngestionResult(
        run_id=f"ingest-{uuid.uuid4().hex[:8]}",
        created_at=created_at,
        manifest_path=str(manifest_path),
        source_count=len(specs),
        record_count=len(records),
        records=records,
    )


def write_result(result: IngestionResult, output_path: Path, pretty: bool = True) -> Path:
    """Write normalized ingestion output to JSON."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        result.model_dump_json(indent=2 if pretty else None),
        encoding="utf-8",
    )
    return output_path