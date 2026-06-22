"""Helpers for loading datasource metadata files."""

from __future__ import annotations

import json
from pathlib import Path

from rag.models import DataSourceMetadata


def load_datasource_metadata(path: Path) -> DataSourceMetadata:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return DataSourceMetadata.model_validate(payload)