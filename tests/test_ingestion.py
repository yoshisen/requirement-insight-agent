import json
from pathlib import Path

from ingestion.pipeline import ingest_from_manifest, write_result
from requirement_insight_agent.cli import main


ROOT = Path(__file__).resolve().parent.parent


def test_ingestion_pipeline_reads_sample_manifest() -> None:
    result = ingest_from_manifest(
        manifest_path=ROOT / "data" / "sample" / "datasource_manifest.json",
        source_root=ROOT / "data" / "sample",
    )

    assert result.source_count == 4
    assert result.record_count == 6
    assert any(record.content_format == "csv_row" for record in result.records)
    assert any(record.content_format == "json_item" for record in result.records)
    assert any(record.content_format == "markdown" for record in result.records)
    assert any(record.content_format == "text" for record in result.records)


def test_ingestion_pipeline_writes_processed_output(tmp_path: Path) -> None:
    result = ingest_from_manifest(
        manifest_path=ROOT / "data" / "sample" / "datasource_manifest.json",
        source_root=ROOT / "data" / "sample",
    )

    output_path = tmp_path / "normalized_records.json"
    write_result(result, output_path)
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert payload["source_count"] == 4
    assert payload["record_count"] == 6
    assert len(payload["records"]) == 6


def test_cli_ingest_command_generates_output(tmp_path: Path) -> None:
    output_path = tmp_path / "cli-normalized.json"

    exit_code = main(
        [
            "ingest",
            "--manifest",
            str(ROOT / "data" / "sample" / "datasource_manifest.json"),
            "--source-root",
            str(ROOT / "data" / "sample"),
            "--output",
            str(output_path),
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert payload["record_count"] == 6