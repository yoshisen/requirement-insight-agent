"""Ingestion package for local source files, manifests, and normalization."""

from .models import IngestionResult, IngestionSourceSpec, NormalizedRecord
from .pipeline import ingest_from_manifest, load_manifest, write_result

__all__ = [
	"IngestionResult",
	"IngestionSourceSpec",
	"NormalizedRecord",
	"ingest_from_manifest",
	"load_manifest",
	"write_result",
]