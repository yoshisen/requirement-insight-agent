"""Reusable end-to-end example workflows for CLI and API entrypoints."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from agents.builders.population_builder import build_population, load_population_config, save_population_result
from evaluation.calibration import (
    build_evaluation_markdown_report,
    evaluate_artifacts,
    save_evaluation_markdown,
    save_evaluation_record,
)
from ingestion.pipeline import ingest_from_manifest, write_result
from rag.indexing.build import build_index_from_processed
from rag.indexing.chunker import ChunkingConfig
from simulations.aggregation import aggregate_run, save_aggregated_output
from simulations.demand.estimator import DemandEstimationInput, build_demand_estimation
from simulations.demand.reporting import save_demand_estimation_bundle
from simulations.inventory.suggestion import build_inventory_suggestion
from simulations.reporting import (
    build_demand_markdown_report,
    build_markdown_report,
    save_markdown_report,
)
from simulations.runner import (
    load_prompt_spec,
    load_scenario_definition,
    run_scenario,
    save_run_result,
)
from requirement_insight_agent.project import PROJECT_ROOT


class ExampleRunConfig(BaseModel):
    """Serializable configuration for running the sample Tokyo supermarket example."""

    model_config = ConfigDict(extra="forbid")

    example_id: str
    manifest_path: str
    source_root: str
    scenario_path: str
    survey_prompt_path: str
    interview_prompt_path: str
    population_config_path: str
    benchmark_path: str
    default_agent_limit: int = Field(ge=1)
    default_base_units: int = Field(ge=1)


class ExampleRunArtifacts(BaseModel):
    """Paths to artifacts produced by one example workflow execution."""

    model_config = ConfigDict(extra="forbid")

    ingest_output: str
    index_dir: str
    population_output: str
    scenario_run_output: str
    scenario_run_jsonl: str
    aggregated_output: str
    aggregation_report: str
    demand_output: str
    demand_report: str
    evaluation_output: str
    evaluation_report: str


def load_example_config(path: Path) -> ExampleRunConfig:
    """Load an example workflow config from JSON."""

    return ExampleRunConfig.model_validate(json.loads(path.read_text(encoding="utf-8")))


def _resolve_repo_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def run_example_workflow(
    *,
    config: ExampleRunConfig,
    output_dir: Path,
    prompt_kind: str = "survey",
    agent_limit: int | None = None,
    base_units: int | None = None,
) -> ExampleRunArtifacts:
    """Execute the full MVP sample pipeline for the Tokyo supermarket launch example."""

    output_dir.mkdir(parents=True, exist_ok=True)
    ingest_output = output_dir / "normalized_records.json"
    index_dir = output_dir / "index"
    population_output = output_dir / "population.json"
    scenario_run_output = output_dir / "scenario_run.json"
    scenario_run_jsonl = output_dir / "scenario_run.jsonl"
    aggregated_output = output_dir / "aggregated_output.json"
    aggregation_report = output_dir / "aggregation_report.md"
    demand_output = output_dir / "demand_estimation.json"
    demand_report = output_dir / "demand_estimation_report.md"
    evaluation_output = output_dir / "evaluation_record.json"
    evaluation_report = output_dir / "evaluation_report.md"

    manifest = _resolve_repo_path(config.manifest_path)
    source_root = _resolve_repo_path(config.source_root)
    ingestion_result = ingest_from_manifest(manifest_path=manifest, source_root=source_root)
    write_result(ingestion_result, ingest_output)

    build_index_from_processed(processed_path=ingest_output, output_dir=index_dir, chunking=ChunkingConfig())

    population_config = load_population_config(_resolve_repo_path(config.population_config_path))
    population = build_population(population_config, sample_size=agent_limit or config.default_agent_limit)
    save_population_result(population, population_output)

    scenario = load_scenario_definition(_resolve_repo_path(config.scenario_path))
    prompt_path = _resolve_repo_path(
        config.survey_prompt_path if prompt_kind == "survey" else config.interview_prompt_path
    )
    prompt_spec = load_prompt_spec(prompt_path)
    run_result = run_scenario(
        scenario=scenario,
        prompt_spec=prompt_spec,
        population=population,
        index_dir=index_dir,
        agent_limit=agent_limit or config.default_agent_limit,
    )
    save_run_result(run_result, scenario_run_output, scenario_run_jsonl)

    aggregated = aggregate_run(run_result=run_result, population=population)
    save_aggregated_output(aggregated, aggregated_output)
    save_markdown_report(build_markdown_report(aggregated), aggregation_report)

    estimation = build_demand_estimation(
        DemandEstimationInput(
            aggregation_output=aggregated,
            base_units_per_period=base_units or config.default_base_units,
            scenario_label=config.example_id,
        )
    )
    inventory_suggestion = build_inventory_suggestion(estimation)
    save_demand_estimation_bundle(estimation, inventory_suggestion, demand_output)
    save_markdown_report(build_demand_markdown_report(estimation, inventory_suggestion), demand_report)

    evaluation_record = evaluate_artifacts(
        population=population,
        aggregated=aggregated,
        benchmark_path=_resolve_repo_path(config.benchmark_path),
    )
    save_evaluation_record(evaluation_record, evaluation_output)
    save_evaluation_markdown(build_evaluation_markdown_report(evaluation_record), evaluation_report)

    return ExampleRunArtifacts(
        ingest_output=str(ingest_output),
        index_dir=str(index_dir),
        population_output=str(population_output),
        scenario_run_output=str(scenario_run_output),
        scenario_run_jsonl=str(scenario_run_jsonl),
        aggregated_output=str(aggregated_output),
        aggregation_report=str(aggregation_report),
        demand_output=str(demand_output),
        demand_report=str(demand_report),
        evaluation_output=str(evaluation_output),
        evaluation_report=str(evaluation_report),
    )