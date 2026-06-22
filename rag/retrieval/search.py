"""Retrieve relevant chunks from the local RAG index bundle."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, field_validator

from rag.indexing.build import FAISS_AVAILABLE, IndexChunkMetadata, IndexManifest, _normalize_vectors
from rag.models import (
    CitationSourceRef,
    CitationTrace,
    CitationTraceMetadata,
    CitationUsedIn,
    RetrievedChunk,
)
from requirement_insight_agent.core.config import AppConfig, load_settings
from requirement_insight_agent.core.providers.factory import create_provider_stack
from requirement_insight_agent.core.providers.models import EmbeddingRequest

try:
    import faiss  # type: ignore
except Exception:  # pragma: no cover
    faiss = None


class RetrievalQuery(BaseModel):
    """Query object for local retrieval tests and grounding."""

    model_config = ConfigDict(extra="forbid")

    query_text: str
    top_k: int = Field(default=5, ge=1)
    min_score: float = Field(default=0.0, ge=0.0, le=1.0)
    region_filters: list[str] = Field(default_factory=list)
    category_filters: list[str] = Field(default_factory=list)
    datasource_filters: list[str] = Field(default_factory=list)
    scenario_id: str = "manual-retrieval"
    agent_id: str | None = None

    @field_validator("query_text")
    @classmethod
    def validate_query_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("query_text must not be empty")
        return value


class RetrievalResultBundle(BaseModel):
    """Structured result of one retrieval call."""

    model_config = ConfigDict(extra="forbid")

    query: RetrievalQuery
    engine: str
    retrieved_chunks: list[RetrievedChunk]
    notes: list[str] = Field(default_factory=list)


def retrieve_chunks(
    *,
    index_dir: Path,
    query: RetrievalQuery,
    settings: AppConfig | None = None,
) -> RetrievalResultBundle:
    """Retrieve relevant chunks from a persisted local index bundle."""

    settings = settings or load_settings()
    manifest = IndexManifest.model_validate(
        json.loads((index_dir / "manifest.json").read_text(encoding="utf-8"))
    )
    metadata = [
        IndexChunkMetadata.model_validate(item)
        for item in json.loads((index_dir / "metadata.json").read_text(encoding="utf-8"))
    ]
    vectors = np.load(index_dir / "vectors.npy")

    candidate_indices = [
        index
        for index, item in enumerate(metadata)
        if _matches_filters(item, query)
    ]

    if not candidate_indices:
        return RetrievalResultBundle(
            query=query,
            engine=manifest.engine,
            retrieved_chunks=[],
            notes=["No indexed chunks matched the provided region/category/datasource filters."],
        )

    provider_stack = create_provider_stack(settings)
    embedding_response = provider_stack.embeddings.embed(
        EmbeddingRequest(texts=[query.query_text], model=settings.resolve_embedding_provider().embedding_model)
    )
    query_vector = np.asarray([embedding_response.vectors[0].values], dtype=np.float32)
    query_vector = _normalize_vectors(query_vector)

    candidate_vectors = vectors[candidate_indices]
    if FAISS_AVAILABLE and faiss is not None and len(candidate_vectors):
        index = faiss.IndexFlatIP(candidate_vectors.shape[1])
        index.add(candidate_vectors.astype(np.float32))
        scores, indices = index.search(query_vector.astype(np.float32), min(query.top_k * 4, len(candidate_indices)))
        ranked_pairs = [(candidate_indices[int(i)], float(score)) for score, i in zip(scores[0], indices[0]) if int(i) >= 0]
        engine = "faiss"
    else:
        scores = candidate_vectors @ query_vector[0]
        ranked_pairs = list(zip(candidate_indices, [float(score) for score in scores]))
        ranked_pairs.sort(key=lambda item: item[1], reverse=True)
        engine = "numpy-fallback"

    results = _rerank_and_build_results(metadata, ranked_pairs, query, top_k=query.top_k, min_score=query.min_score)
    notes = []
    if not results:
        notes.append("No chunks passed the score threshold after retrieval.")
    return RetrievalResultBundle(query=query, engine=engine, retrieved_chunks=results, notes=notes)


def _matches_filters(item: IndexChunkMetadata, query: RetrievalQuery) -> bool:
    if query.region_filters and not any(region in item.region_tags for region in query.region_filters):
        return False
    if query.category_filters and not any(category in item.category_tags for category in query.category_filters):
        return False
    if query.datasource_filters and item.datasource_id not in query.datasource_filters:
        return False
    return True


def _rerank_and_build_results(
    metadata: list[IndexChunkMetadata],
    ranked_pairs: list[tuple[int, float]],
    query: RetrievalQuery,
    *,
    top_k: int,
    min_score: float,
) -> list[RetrievedChunk]:
    query_tokens = _tokenize(query.query_text)
    rescored: list[tuple[IndexChunkMetadata, float]] = []

    for metadata_index, vector_score in ranked_pairs:
        item = metadata[metadata_index]
        lexical_score = _lexical_overlap(query_tokens, _tokenize(item.text))
        combined_score = max(0.0, min(1.0, 0.7 * vector_score + 0.3 * lexical_score))
        if combined_score >= min_score:
            rescored.append((item, combined_score))

    rescored.sort(key=lambda pair: pair[1], reverse=True)

    retrieved: list[RetrievedChunk] = []
    now = datetime.now(timezone.utc)
    for item, score in rescored[:top_k]:
        trace = CitationTrace(
            trace_id=f"trace::{item.chunk_id}",
            source_ref=CitationSourceRef(
                datasource_id=item.datasource_id,
                document_id=item.record_id,
                chunk_id=item.chunk_id,
            ),
            used_in=CitationUsedIn(
                scenario_id=query.scenario_id,
                agent_id=query.agent_id,
            ),
            citation_text=item.text,
            relevance_score=score,
            metadata=CitationTraceMetadata(
                retrieved_at=now,
                retrieval_method="faiss_hybrid" if FAISS_AVAILABLE else "numpy_hybrid",
                region_filter=",".join(query.region_filters) or None,
                category_filter=",".join(query.category_filters) or None,
            ),
        )
        retrieved.append(
            RetrievedChunk(
                chunk_id=item.chunk_id,
                document_id=item.record_id,
                datasource_id=item.datasource_id,
                title=item.title,
                source_type=item.source_type,
                text=item.text,
                region_tags=item.region_tags,
                category_tags=item.category_tags,
                score=score,
                citation_trace=trace,
            )
        )
    return retrieved


def _tokenize(text: str) -> set[str]:
    return {token for token in re.split(r"[^\w\u3040-\u30ff\u3400-\u9fff]+", text.lower()) if token}


def _lexical_overlap(query_tokens: set[str], candidate_tokens: set[str]) -> float:
    if not query_tokens:
        return 0.0
    return len(query_tokens & candidate_tokens) / len(query_tokens)