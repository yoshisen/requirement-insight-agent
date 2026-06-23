import json
from pathlib import Path

from ingestion.models import IngestionResult
from rag.indexing.chunker import ChunkingConfig, chunk_normalized_records


ROOT = Path(__file__).resolve().parent.parent


def test_chunk_normalized_records_from_processed_output() -> None:
    payload = json.loads(
        (ROOT / "data" / "processed" / "normalized_records.json").read_text(encoding="utf-8")
    )
    result = IngestionResult.model_validate(payload)

    chunks = chunk_normalized_records(result.records, ChunkingConfig(chunk_size=80, chunk_overlap=20))

    assert chunks
    assert any(chunk.datasource_id == "tokyo-market-note-001" for chunk in chunks)
    assert all(chunk.chunk_count >= 1 for chunk in chunks)


def test_chunking_preserves_region_and_category_tags() -> None:
    payload = json.loads(
        (ROOT / "data" / "processed" / "normalized_records.json").read_text(encoding="utf-8")
    )
    result = IngestionResult.model_validate(payload)

    chunks = chunk_normalized_records(result.records, ChunkingConfig(chunk_size=100, chunk_overlap=10))
    first = chunks[0]

    assert "tokyo-metropolitan" in first.region_tags
    assert first.category_tags