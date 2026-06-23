"""Minimal CLI entry points for the repository scaffold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from agents.builders.population_builder import build_population, load_population_config, save_population_result
from evaluation.calibration import (
    build_evaluation_markdown_report,
    evaluate_artifacts,
    load_aggregated_output as load_evaluation_aggregated_output,
    load_population_result as load_evaluation_population_result,
    save_evaluation_markdown,
    save_evaluation_record,
)
from ingestion.pipeline import ingest_from_manifest, write_result
from rag.grounding.builder import build_grounding_context
from rag.indexing.build import build_index_from_processed
from rag.indexing.chunker import ChunkingConfig
from rag.retrieval.search import RetrievalQuery, retrieve_chunks
from requirement_insight_agent import __version__
from requirement_insight_agent.project import PROJECT_ROOT, SCAFFOLD_PATHS, scaffold_status
from requirement_insight_agent.workflows import load_example_config, run_example_workflow
from simulations.aggregation import aggregate_run, load_aggregated_output, load_run_result, save_aggregated_output
from simulations.demand.estimator import DemandEstimationInput, build_demand_estimation
from simulations.demand.reporting import save_demand_estimation_bundle
from simulations.inventory.suggestion import build_inventory_suggestion
from simulations.reporting import build_demand_markdown_report, build_markdown_report, save_markdown_report
from simulations.runner import (
    load_population_result,
    load_prompt_spec,
    load_scenario_definition,
    run_scenario,
    save_run_result,
)


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

    population_parser = subparsers.add_parser(
        "build-population",
        help="Generate a synthetic consumer population from a weighted config.",
    )
    population_parser.add_argument(
        "--config",
        type=Path,
        default=PROJECT_ROOT / "configs" / "populations" / "tokyo_mvp_population.json",
        help="Path to the population configuration JSON file.",
    )
    population_parser.add_argument(
        "--sample-size",
        type=int,
        default=None,
        help="Optional override for the number of agents to generate.",
    )
    population_parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Optional override for category conditioning.",
    )
    population_parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "agents" / "sample_profiles" / "tokyo_mvp_population.sample.json",
        help="Path to the generated population JSON output.",
    )

    scenario_parser = subparsers.add_parser(
        "run-scenario",
        help="Run a survey or interview prompt against a synthetic population.",
    )
    scenario_parser.add_argument(
        "--scenario",
        type=Path,
        default=PROJECT_ROOT / "examples" / "tokyo-supermarket-launch" / "scenario.json",
        help="Path to the scenario definition JSON file.",
    )
    scenario_parser.add_argument(
        "--prompt",
        type=Path,
        default=PROJECT_ROOT / "prompts" / "survey" / "supermarket-launch-survey-v1.json",
        help="Path to the prompt spec JSON file.",
    )
    scenario_parser.add_argument(
        "--population",
        type=Path,
        default=PROJECT_ROOT / "agents" / "sample_profiles" / "tokyo_mvp_population.sample.json",
        help="Path to the generated synthetic population JSON file.",
    )
    scenario_parser.add_argument(
        "--index-dir",
        type=Path,
        default=PROJECT_ROOT / ".local" / "index" / "sample",
        help="Path to the local RAG index bundle directory.",
    )
    scenario_parser.add_argument(
        "--agent-limit",
        type=int,
        default=5,
        help="How many agents to execute in this run.",
    )
    scenario_parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / ".local" / "output" / "scenario_run.json",
        help="Path to the structured scenario run JSON output.",
    )
    scenario_parser.add_argument(
        "--jsonl-output",
        type=Path,
        default=PROJECT_ROOT / ".local" / "output" / "scenario_run.jsonl",
        help="Optional path to JSONL per-agent response output.",
    )

    aggregate_parser = subparsers.add_parser(
        "aggregate",
        help="Aggregate a scenario run into machine-readable JSON and markdown report.",
    )
    aggregate_parser.add_argument(
        "--run-result",
        type=Path,
        default=PROJECT_ROOT / ".local" / "output" / "scenario_run.json",
        help="Path to the scenario run JSON file.",
    )
    aggregate_parser.add_argument(
        "--population",
        type=Path,
        default=PROJECT_ROOT / "agents" / "sample_profiles" / "tokyo_mvp_population.sample.json",
        help="Path to the generated synthetic population JSON file.",
    )
    aggregate_parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / ".local" / "output" / "aggregated_output.json",
        help="Path to the aggregated machine-readable JSON output.",
    )
    aggregate_parser.add_argument(
        "--report",
        type=Path,
        default=PROJECT_ROOT / ".local" / "output" / "aggregation_report.md",
        help="Path to the human-readable markdown report.",
    )

    evaluate_parser = subparsers.add_parser(
        "evaluate",
        help="Evaluate population and aggregated outputs against a benchmark.",
    )
    evaluate_parser.add_argument(
        "--population",
        type=Path,
        default=PROJECT_ROOT / "agents" / "sample_profiles" / "tokyo_mvp_population.sample.json",
        help="Path to the generated population JSON file.",
    )
    evaluate_parser.add_argument(
        "--aggregation",
        type=Path,
        default=PROJECT_ROOT / ".local" / "output" / "aggregated_output.json",
        help="Path to the aggregated output JSON file.",
    )
    evaluate_parser.add_argument(
        "--benchmark",
        type=Path,
        default=PROJECT_ROOT / "evaluation" / "benchmarks" / "tokyo_mvp_expected_distribution.json",
        help="Path to the benchmark distribution JSON file.",
    )
    evaluate_parser.add_argument(
        "--comparison-output",
        type=Path,
        default=None,
        help="Optional second aggregated output file for a simple stability comparison.",
    )
    evaluate_parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / ".local" / "output" / "evaluation_record.json",
        help="Path to the machine-readable evaluation JSON output.",
    )
    evaluate_parser.add_argument(
        "--report",
        type=Path,
        default=PROJECT_ROOT / ".local" / "output" / "evaluation_report.md",
        help="Path to the human-readable evaluation markdown report.",
    )

    demand_parser = subparsers.add_parser(
        "estimate-demand",
        help="Estimate demand ranges and inventory suggestion from an aggregated output.",
    )
    demand_parser.add_argument(
        "--aggregation",
        type=Path,
        default=PROJECT_ROOT / ".local" / "output" / "aggregated_output.json",
        help="Path to the aggregated output JSON file.",
    )
    demand_parser.add_argument(
        "--base-units",
        type=int,
        default=1000,
        help="Scenario anchor used by the demand heuristic.",
    )
    demand_parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / ".local" / "output" / "demand_estimation.json",
        help="Path to the machine-readable demand estimation JSON output.",
    )
    demand_parser.add_argument(
        "--report",
        type=Path,
        default=PROJECT_ROOT / ".local" / "output" / "demand_estimation_report.md",
        help="Path to the human-readable markdown demand report.",
    )

    run_example_parser = subparsers.add_parser(
        "run-example",
        help="Run the Tokyo supermarket launch sample flow end-to-end.",
    )
    run_example_parser.add_argument(
        "--config",
        type=Path,
        default=PROJECT_ROOT / "examples" / "tokyo-supermarket-launch" / "example_config.json",
        help="Path to the example workflow configuration JSON.",
    )
    run_example_parser.add_argument(
        "--prompt-kind",
        choices=["survey", "interview"],
        default="survey",
        help="Which prompt flow to run for the example.",
    )
    run_example_parser.add_argument(
        "--agent-limit",
        type=int,
        default=None,
        help="Optional override for the number of agents used in the example run.",
    )
    run_example_parser.add_argument(
        "--base-units",
        type=int,
        default=None,
        help="Optional override for the demand estimation baseline units.",
    )
    run_example_parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / ".local" / "examples" / "tokyo-supermarket-launch",
        help="Directory where example artifacts are written.",
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


def cmd_build_population(
    config_path: Path,
    sample_size: int | None,
    category: str | None,
    output: Path,
) -> int:
    config = load_population_config(config_path)
    result = build_population(config, sample_size=sample_size, category=category)
    written_path = save_population_result(result, output)

    print("Requirement Insight Agent population build result")
    print(f"- config: {config_path}")
    print(f"- sample_size: {result.sample_size}")
    print(f"- category: {result.category}")
    print(f"- output: {written_path}")

    return 0


def cmd_run_scenario(
    scenario_path: Path,
    prompt_path: Path,
    population_path: Path,
    index_dir: Path,
    agent_limit: int,
    output: Path,
    jsonl_output: Path | None,
) -> int:
    scenario = load_scenario_definition(scenario_path)
    prompt_spec = load_prompt_spec(prompt_path)
    population = load_population_result(population_path)
    result = run_scenario(
        scenario=scenario,
        prompt_spec=prompt_spec,
        population=population,
        index_dir=index_dir,
        agent_limit=agent_limit,
    )
    save_run_result(result, output, jsonl_output)

    print("Requirement Insight Agent scenario run result")
    print(f"- scenario: {scenario_path}")
    print(f"- prompt: {prompt_path}")
    print(f"- agent_limit: {agent_limit}")
    print(f"- response_count: {result.response_count}")
    print(f"- output: {output}")
    if jsonl_output is not None:
        print(f"- jsonl_output: {jsonl_output}")

    return 0


def cmd_aggregate(
    run_result_path: Path,
    population_path: Path,
    output: Path,
    report: Path,
) -> int:
    run_result = load_run_result(run_result_path)
    population = load_population_result(population_path)
    aggregated = aggregate_run(run_result=run_result, population=population)
    save_aggregated_output(aggregated, output)
    report_text = build_markdown_report(aggregated)
    save_markdown_report(report_text, report)

    print("Requirement Insight Agent aggregation result")
    print(f"- run_result: {run_result_path}")
    print(f"- population: {population_path}")
    print(f"- output: {output}")
    print(f"- report: {report}")
    print(f"- segment_count: {len(aggregated.segment_summaries)}")
    print(f"- citation_count: {len(aggregated.citation_summary)}")

    return 0


def cmd_estimate_demand(
    aggregation_path: Path,
    base_units: int,
    output: Path,
    report: Path,
) -> int:
    aggregated = load_aggregated_output(aggregation_path)
    estimation = build_demand_estimation(
        DemandEstimationInput(
            aggregation_output=aggregated,
            base_units_per_period=base_units,
            scenario_label="cli-run",
        )
    )
    inventory_suggestion = build_inventory_suggestion(estimation)
    save_demand_estimation_bundle(estimation, inventory_suggestion, output)
    save_markdown_report(build_demand_markdown_report(estimation, inventory_suggestion), report)

    print("Requirement Insight Agent demand estimation result")
    print(f"- aggregation: {aggregation_path}")
    print(f"- output: {output}")
    print(f"- report: {report}")
    print(f"- confidence: {estimation.confidence}")
    print(f"- warnings: {len(estimation.warnings)}")

    return 0


def cmd_evaluate(
    population_path: Path,
    aggregation_path: Path,
    benchmark_path: Path,
    comparison_output: Path | None,
    output: Path,
    report: Path,
) -> int:
    population = load_evaluation_population_result(population_path)
    aggregated = load_evaluation_aggregated_output(aggregation_path)
    comparison = load_evaluation_aggregated_output(comparison_output) if comparison_output else None
    record = evaluate_artifacts(
        population=population,
        aggregated=aggregated,
        benchmark_path=benchmark_path,
        comparison_output=comparison,
    )
    save_evaluation_record(record, output)
    save_evaluation_markdown(build_evaluation_markdown_report(record), report)

    print("Requirement Insight Agent evaluation result")
    print(f"- population: {population_path}")
    print(f"- aggregation: {aggregation_path}")
    print(f"- benchmark: {benchmark_path}")
    print(f"- output: {output}")
    print(f"- report: {report}")
    print(f"- representativeness_score: {record.metrics.representativeness_score}")
    print(f"- stability_score: {record.metrics.stability_score}")

    return 0


def cmd_run_example(
    config_path: Path,
    prompt_kind: str,
    agent_limit: int | None,
    base_units: int | None,
    output_dir: Path,
) -> int:
    config = load_example_config(config_path)
    artifacts = run_example_workflow(
        config=config,
        output_dir=output_dir,
        prompt_kind=prompt_kind,
        agent_limit=agent_limit,
        base_units=base_units,
    )

    print("Requirement Insight Agent example run result")
    print(f"- config: {config_path}")
    print(f"- prompt_kind: {prompt_kind}")
    print(f"- output_dir: {output_dir}")
    print(f"- aggregated_output: {artifacts.aggregated_output}")
    print(f"- demand_output: {artifacts.demand_output}")
    print(f"- evaluation_output: {artifacts.evaluation_output}")

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

    if args.command == "build-population":
        return cmd_build_population(args.config, args.sample_size, args.category, args.output)

    if args.command == "run-scenario":
        return cmd_run_scenario(
            args.scenario,
            args.prompt,
            args.population,
            args.index_dir,
            args.agent_limit,
            args.output,
            args.jsonl_output,
        )

    if args.command == "aggregate":
        return cmd_aggregate(args.run_result, args.population, args.output, args.report)

    if args.command == "evaluate":
        return cmd_evaluate(
            args.population,
            args.aggregation,
            args.benchmark,
            args.comparison_output,
            args.output,
            args.report,
        )

    if args.command == "estimate-demand":
        return cmd_estimate_demand(args.aggregation, args.base_units, args.output, args.report)

    if args.command == "run-example":
        return cmd_run_example(
            args.config,
            args.prompt_kind,
            args.agent_limit,
            args.base_units,
            args.output_dir,
        )

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())