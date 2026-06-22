"""Local file loaders for ingestion MVP.

Supported file types:
- CSV
- JSON
- Markdown
- Plain text
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from ingestion.models import IngestionSourceSpec, LoadedRecord, LoaderHint


def detect_loader_hint(source_path: Path, explicit_hint: LoaderHint | None = None) -> LoaderHint:
    """Resolve the loader type from an explicit hint or file extension."""

    if explicit_hint is not None:
        return explicit_hint

    suffix = source_path.suffix.lower()
    if suffix == ".csv":
        return "csv"
    if suffix == ".json":
        return "json"
    if suffix in {".md", ".markdown"}:
        return "markdown"
    if suffix == ".txt":
        return "text"

    raise ValueError(f"Unsupported source file type: {source_path}")


def load_records(spec: IngestionSourceSpec, source_path: Path) -> list[LoadedRecord]:
    """Load a source file into intermediate records."""

    hint = detect_loader_hint(source_path, spec.loader_hint)

    if hint == "csv":
        return _load_csv(spec, source_path)
    if hint == "json":
        return _load_json(spec, source_path)
    if hint == "markdown":
        return _load_markdown(spec, source_path)
    if hint == "text":
        return _load_text(spec, source_path)

    raise ValueError(f"Unhandled loader hint: {hint}")


def _load_csv(spec: IngestionSourceSpec, source_path: Path) -> list[LoadedRecord]:
    records: list[LoadedRecord] = []

    with source_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader):
            title = _resolve_title(spec, row, fallback=f"row-{index}")
            text = _resolve_text(spec, row)
            records.append(
                LoadedRecord(
                    local_id=f"row-{index}",
                    content_format="csv_row",
                    title=title,
                    text=text,
                    structured_data=row,
                )
            )

    return records


def _load_json(spec: IngestionSourceSpec, source_path: Path) -> list[LoadedRecord]:
    payload = json.loads(source_path.read_text(encoding="utf-8"))

    if isinstance(payload, list):
        records: list[LoadedRecord] = []
        for index, item in enumerate(payload):
            item_dict = item if isinstance(item, dict) else {"value": item}
            title = _resolve_title(spec, item_dict, fallback=f"item-{index}")
            text = _resolve_text(spec, item_dict)
            records.append(
                LoadedRecord(
                    local_id=f"item-{index}",
                    content_format="json_item",
                    title=title,
                    text=text,
                    structured_data=item_dict,
                )
            )
        return records

    payload_dict = payload if isinstance(payload, dict) else {"value": payload}
    return [
        LoadedRecord(
            local_id="object-0",
            content_format="json_object",
            title=_resolve_title(spec, payload_dict, fallback=source_path.stem),
            text=_resolve_text(spec, payload_dict),
            structured_data=payload_dict,
        )
    ]


def _load_markdown(spec: IngestionSourceSpec, source_path: Path) -> list[LoadedRecord]:
    text = source_path.read_text(encoding="utf-8")
    title = _extract_markdown_title(text) or source_path.stem
    return [
        LoadedRecord(
            local_id="markdown-0",
            content_format="markdown",
            title=title,
            text=text,
        )
    ]


def _load_text(spec: IngestionSourceSpec, source_path: Path) -> list[LoadedRecord]:
    text = source_path.read_text(encoding="utf-8")
    return [
        LoadedRecord(
            local_id="text-0",
            content_format="text",
            title=source_path.stem,
            text=text,
        )
    ]


def _resolve_title(spec: IngestionSourceSpec, data: dict[str, Any], fallback: str) -> str:
    if spec.title_field and data.get(spec.title_field):
        return str(data[spec.title_field])

    for value in data.values():
        if value not in (None, ""):
            return str(value)

    return fallback


def _resolve_text(spec: IngestionSourceSpec, data: dict[str, Any]) -> str:
    if spec.text_fields:
        selected = [f"{field}: {data[field]}" for field in spec.text_fields if field in data]
        if selected:
            return "\n".join(selected)

    return "\n".join(f"{key}: {value}" for key, value in data.items())


def _extract_markdown_title(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("# ")
    return None