import json
from pathlib import Path

from rag.grounding.builder import build_grounding_context
from rag.indexing.build import build_index_from_processed
from rag.indexing.chunker import ChunkingConfig
from rag.retrieval.search import RetrievalQuery, retrieve_chunks
from requirement_insight_agent.cli import main


ROOT = Path(__file__).resolve().parent.parent


def test_build_index_from_processed_creates_bundle(tmp_path: Path) -> None:
    manifest = build_index_from_processed(
        processed_path=ROOT / "data" / "processed" / "normalized_records.json",
        output_dir=tmp_path,
        chunking=ChunkingConfig(chunk_size=90, chunk_overlap=20),
    )

    assert manifest.chunk_count > 0
    assert (tmp_path / "manifest.json").exists()
    assert (tmp_path / "metadata.json").exists()
    assert (tmp_path / "vectors.npy").exists()


def test_retrieve_chunks_with_region_and_category_filters(tmp_path: Path) -> None:
    build_index_from_processed(
        processed_path=ROOT / "data" / "processed" / "normalized_records.json",
        output_dir=tmp_path,
        chunking=ChunkingConfig(chunk_size=90, chunk_overlap=20),
    )
    query = RetrievalQuery(
        query_text="high protein frozen food quick meal tokyo",
        region_filters=["tokyo-metropolitan"],
        category_filters=["frozen_food"],
        top_k=3,
        min_score=0.01,
        scenario_id="tokyo-frozen-protein-launch-v1",
    )

    result = retrieve_chunks(index_dir=tmp_path, query=query)

    assert result.retrieved_chunks
    assert all("tokyo-metropolitan" in chunk.region_tags for chunk in result.retrieved_chunks)
    assert all("frozen_food" in chunk.category_tags for chunk in result.retrieved_chunks)


def test_grounding_context_marks_uncertainty_for_no_results(tmp_path: Path) -> None:
    build_index_from_processed(
        processed_path=ROOT / "data" / "processed" / "normalized_records.json",
        output_dir=tmp_path,
    )
    query = RetrievalQuery(
        query_text="nonexistent signal",
        region_filters=["nonexistent-region"],
        top_k=3,
        scenario_id="tokyo-frozen-protein-launch-v1",
    )

    result = retrieve_chunks(index_dir=tmp_path, query=query)
    context = build_grounding_context(query, result.retrieved_chunks)

    assert context.overall_uncertainty == "high"
    assert context.notes


def test_cli_build_index_and_retrieve_test(tmp_path: Path) -> None:
    index_dir = tmp_path / "index"
    result_path = tmp_path / "retrieval_result.json"

    build_exit = main(
        [
            "build-index",
            "--input",
            str(ROOT / "data" / "processed" / "normalized_records.json"),
            "--output-dir",
            str(index_dir),
            "--chunk-size",
            "90",
            "--chunk-overlap",
            "20",
        ]
    )
    retrieve_exit = main(
        [
            "retrieve-test",
            "--index-dir",
            str(index_dir),
            "--query-file",
            str(ROOT / "examples" / "tokyo-supermarket-launch" / "retrieval_query.json"),
            "--output",
            str(result_path),
        ]
    )

    payload = json.loads(result_path.read_text(encoding="utf-8"))

    assert build_exit == 0
    assert retrieve_exit == 0
    assert "retrieval" in payload
    assert "grounding_context" in payload