"""Build a local retrieval index from normalized ingestion output."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import numpy as np
from pydantic import BaseModel, ConfigDict, Field

from ingestion.models import IngestionResult
from rag.indexing.chunker import ChunkRecord, ChunkingConfig, chunk_normalized_records
from requirement_insight_agent.core.config import AppConfig, load_settings
from requirement_insight_agent.core.providers.factory import create_provider_stack
from requirement_insight_agent.core.providers.models import EmbeddingRequest

try:
    import faiss  # type: ignore

    FAISS_AVAILABLE = True
except Exception:  # pragma: no cover - fallback path is tested functionally
    faiss = None
    FAISS_AVAILABLE = False


IndexEngine = Literal["faiss", "numpy-fallback"]


class IndexChunkMetadata(BaseModel):
    """Stored metadata for one indexed chunk."""

    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    record_id: str
    datasource_id: str
    source_type: str
    title: str
    region_tags: list[str] = Field(default_factory=list)
    category_tags: list[str] = Field(default_factory=list)
    quality_score: float
    text: str


class IndexManifest(BaseModel):
    """Manifest describing a persisted local RAG index bundle."""

    model_config = ConfigDict(extra="forbid")

    index_id: str
    created_at: datetime
    source_path: str
    chunk_count: int
    vector_dimension: int
    engine: IndexEngine
    embedding_provider: str
    embedding_model: str
    files: dict[str, str]
    notes: list[str] = Field(default_factory=list)


def build_index_from_processed(
    *,
    processed_path: Path,
    output_dir: Path,
    chunking: ChunkingConfig | None = None,
    settings: AppConfig | None = None,
) -> IndexManifest:
    """Build a persisted local retrieval index from normalized ingestion output."""

    chunking = chunking or ChunkingConfig()
    settings = settings or load_settings()
    payload = json.loads(processed_path.read_text(encoding="utf-8"))
    ingested = IngestionResult.model_validate(payload)
    chunks = chunk_normalized_records(ingested.records, chunking)

    provider_stack = create_provider_stack(settings)
    embedding_request = EmbeddingRequest(
        texts=[chunk.text for chunk in chunks],
        model=settings.resolve_embedding_provider().embedding_model,
        metadata={"source": str(processed_path)},
    )
    embedding_response = provider_stack.embeddings.embed(embedding_request)

    vectors = np.asarray([vector.values for vector in embedding_response.vectors], dtype=np.float32)
    vectors = _normalize_vectors(vectors)

    output_dir.mkdir(parents=True, exist_ok=True)

    engine: IndexEngine = "faiss" if FAISS_AVAILABLE else "numpy-fallback"
    metadata = [
        IndexChunkMetadata(
            chunk_id=chunk.chunk_id,
            record_id=chunk.record_id,
            datasource_id=chunk.datasource_id,
            source_type=chunk.source_type,
            title=chunk.title,
            region_tags=chunk.region_tags,
            category_tags=chunk.category_tags,
            quality_score=chunk.quality_score,
            text=chunk.text,
        )
        for chunk in chunks
    ]

    manifest = IndexManifest(
        index_id=f"rag-index-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        created_at=datetime.now(timezone.utc),
        source_path=str(processed_path),
        chunk_count=len(chunks),
        vector_dimension=int(vectors.shape[1]) if len(vectors) else 0,
        engine=engine,
        embedding_provider=embedding_response.provider,
        embedding_model=embedding_response.model,
        files={
            "manifest": "manifest.json",
            "metadata": "metadata.json",
            "vectors": "vectors.npy",
            "faiss_index": "index.faiss",
        },
        notes=[
            "FAISS is used when available; numpy fallback remains available for portability.",
            "Vectors are normalized for cosine-style similarity search.",
        ],
    )

    (output_dir / "manifest.json").write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    (output_dir / "metadata.json").write_text(
        json.dumps([item.model_dump(mode="json") for item in metadata], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    np.save(output_dir / "vectors.npy", vectors)

    if FAISS_AVAILABLE and len(vectors):
        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)
        faiss.write_index(index, str(output_dir / "index.faiss"))
    else:
        (output_dir / "index.faiss").write_bytes(b"")

    return manifest


def _normalize_vectors(vectors: np.ndarray) -> np.ndarray:
    if vectors.size == 0:
        return vectors
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vectors / norms