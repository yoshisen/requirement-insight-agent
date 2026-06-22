"""Minimal CLI entry points for the repository scaffold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from ingestion.pipeline import ingest_from_manifest, write_result
from rag.grounding.builder import build_grounding_context
from rag.indexing.build import build_index_from_processed
from rag.indexing.chunker import ChunkingConfig
from rag.retrieval.search import RetrievalQuery, retrieve_chunks
from requirement_insight_agent import __version__
from requirement_insight_agent.project import PROJECT_ROOT, SCAFFOLD_PATHS, scaffold_status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ria",
        description="Requirement Insight Agent scaffold utilities.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Show whether the expected scaffold paths exist.")
    subparsers.add_parser("paths", help="Print key repository paths.")

    ingest_parser = subparsers.add_parser("ingest", help="Ingest local sample or user-provided data.")
    ingest_parser.add_argument(
        "--manifest",
        type=Path,
        default=PROJECT_ROOT / "data" / "sample" / "datasource_manifest.json",
        help="Path to the datasource manifest JSON file.",
    )
    ingest_parser.add_argument(
        "--source-root",
        type=Path,
        default=PROJECT_ROOT / "data" / "sample",
        help="Root directory used to resolve source_path entries.",
    )
    ingest_parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "normalized_records.json",
        help="Path to the normalized JSON output file.",
    )
    ingest_parser.add_argument(
        "--compact",
        action="store_true",
        help="Write compact JSON instead of pretty-printed JSON.",
    )

    build_index_parser = subparsers.add_parser("build-index", help="Build a local RAG index bundle.")
    build_index_parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "data" / "processed" / "normalized_records.json",
        help="Path to normalized ingestion output JSON.",
    )
    build_index_parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / ".local" / "index" / "sample",
        help="Directory where the local index bundle is written.",
    )
    build_index_parser.add_argument(
        "--chunk-size",
        type=int,
        default=220,
        help="Chunk size for retrieval documents.",
    )
    build_index_parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=40,
        help="Chunk overlap for retrieval documents.",
    )

    retrieve_parser = subparsers.add_parser("retrieve-test", help="Run a local retrieval test against the index.")
    retrieve_parser.add_argument(
        "--index-dir",
        type=Path,
        default=PROJECT_ROOT / ".local" / "index" / "sample",
        help="Directory containing the local index bundle.",
    )
    retrieve_parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Inline retrieval query text.",
    )
    retrieve_parser.add_argument(
        "--query-file",
        type=Path,
        default=PROJECT_ROOT / "examples" / "tokyo-supermarket-launch" / "retrieval_query.json",
        help="JSON file containing a RetrievalQuery payload.",
    )
    retrieve_parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / ".local" / "output" / "retrieval_result.json",
        help="Where to write the retrieval and grounding result JSON.",
    )

    return parser


def cmd_status() -> int:
    print("Requirement Insight Agent scaffold status")
    print(f"project_root: {PROJECT_ROOT}")

    for name, exists in scaffold_status().items():
        state = "present" if exists else "missing"
        print(f"- {name}: {state}")

    return 0


def cmd_paths() -> int:
    for name, path in SCAFFOLD_PATHS.items():
        rel_path = path.relative_to(PROJECT_ROOT)
        print(f"{name}: {rel_path}")

    return 0


def cmd_ingest(manifest: Path, source_root: Path, output: Path, compact: bool) -> int:
    result = ingest_from_manifest(manifest_path=manifest, source_root=source_root)
    written_path = write_result(result, output, pretty=not compact)

    print("Requirement Insight Agent ingestion result")
    print(f"- manifest: {manifest}")
    print(f"- source_count: {result.source_count}")
    print(f"- record_count: {result.record_count}")
    print(f"- output: {written_path}")

    return 0


def cmd_build_index(input_path: Path, output_dir: Path, chunk_size: int, chunk_overlap: int) -> int:
    manifest = build_index_from_processed(
        processed_path=input_path,
        output_dir=output_dir,
        chunking=ChunkingConfig(chunk_size=chunk_size, chunk_overlap=chunk_overlap),
    )

    print("Requirement Insight Agent index build result")
    print(f"- input: {input_path}")
    print(f"- chunk_count: {manifest.chunk_count}")
    print(f"- vector_dimension: {manifest.vector_dimension}")
    print(f"- engine: {manifest.engine}")
    print(f"- output_dir: {output_dir}")

    return 0


def cmd_retrieve_test(index_dir: Path, query: str | None, query_file: Path, output: Path) -> int:
    if query is not None:
        retrieval_query = RetrievalQuery(query_text=query)
    else:
        payload = json.loads(query_file.read_text(encoding="utf-8"))
        retrieval_query = RetrievalQuery.model_validate(payload)

    result = retrieve_chunks(index_dir=index_dir, query=retrieval_query)
    grounding_context = build_grounding_context(retrieval_query, result.retrieved_chunks)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "retrieval": result.model_dump(mode="json"),
                "grounding_context": grounding_context.model_dump(mode="json"),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("Requirement Insight Agent retrieval result")
    print(f"- query: {retrieval_query.query_text}")
    print(f"- retrieved_chunks: {len(result.retrieved_chunks)}")
    print(f"- uncertainty: {grounding_context.overall_uncertainty}")
    print(f"- output: {output}")

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "status":
        return cmd_status()

    if args.command == "paths":
        return cmd_paths()

    if args.command == "ingest":
        return cmd_ingest(args.manifest, args.source_root, args.output, args.compact)

    if args.command == "build-index":
        return cmd_build_index(args.input, args.output_dir, args.chunk_size, args.chunk_overlap)

    if args.command == "retrieve-test":
        return cmd_retrieve_test(args.index_dir, args.query, args.query_file, args.output)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())