"""Typer-based unified CLI entrypoint for Requirement Insight Agent."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from requirement_insight_agent import __version__
from requirement_insight_agent import cli as backend
from requirement_insight_agent.project import PROJECT_ROOT


app = typer.Typer(help="Requirement Insight Agent end-to-end CLI.")


@app.callback(invoke_without_command=True)
def _root(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Show the CLI version and exit."),
) -> None:
    if version:
        typer.echo(f"ria {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


@app.command("status")
def status() -> None:
    raise typer.Exit(code=backend.cmd_status())


@app.command("paths")
def paths() -> None:
    raise typer.Exit(code=backend.cmd_paths())


@app.command("ingest")
def ingest(
    manifest: Path = typer.Option(PROJECT_ROOT / "data" / "sample" / "datasource_manifest.json"),
    source_root: Path = typer.Option(PROJECT_ROOT / "data" / "sample"),
    output: Path = typer.Option(PROJECT_ROOT / "data" / "processed" / "normalized_records.json"),
    compact: bool = typer.Option(False, help="Write compact JSON instead of pretty JSON."),
) -> None:
    raise typer.Exit(code=backend.cmd_ingest(manifest, source_root, output, compact))


@app.command("build-index")
def build_index(
    input: Path = typer.Option(PROJECT_ROOT / "data" / "processed" / "normalized_records.json"),
    output_dir: Path = typer.Option(PROJECT_ROOT / ".local" / "index" / "sample"),
    chunk_size: int = typer.Option(220),
    chunk_overlap: int = typer.Option(40),
) -> None:
    raise typer.Exit(code=backend.cmd_build_index(input, output_dir, chunk_size, chunk_overlap))


@app.command("retrieve-test")
def retrieve_test(
    index_dir: Path = typer.Option(PROJECT_ROOT / ".local" / "index" / "sample"),
    query: Optional[str] = typer.Option(None),
    query_file: Path = typer.Option(PROJECT_ROOT / "examples" / "tokyo-supermarket-launch" / "retrieval_query.json"),
    output: Path = typer.Option(PROJECT_ROOT / ".local" / "output" / "retrieval_result.json"),
) -> None:
    raise typer.Exit(code=backend.cmd_retrieve_test(index_dir, query, query_file, output))


@app.command("build-population")
def build_population(
    config: Path = typer.Option(PROJECT_ROOT / "configs" / "populations" / "tokyo_mvp_population.json"),
    sample_size: Optional[int] = typer.Option(None),
    category: Optional[str] = typer.Option(None),
    output: Path = typer.Option(PROJECT_ROOT / "agents" / "sample_profiles" / "tokyo_mvp_population.sample.json"),
) -> None:
    raise typer.Exit(code=backend.cmd_build_population(config, sample_size, category, output))


@app.command("run-scenario")
def run_scenario(
    scenario: Path = typer.Option(PROJECT_ROOT / "examples" / "tokyo-supermarket-launch" / "scenario.json"),
    prompt: Path = typer.Option(PROJECT_ROOT / "prompts" / "survey" / "supermarket-launch-survey-v1.json"),
    population: Path = typer.Option(PROJECT_ROOT / "agents" / "sample_profiles" / "tokyo_mvp_population.sample.json"),
    index_dir: Path = typer.Option(PROJECT_ROOT / ".local" / "index" / "sample"),
    agent_limit: int = typer.Option(5),
    output: Path = typer.Option(PROJECT_ROOT / ".local" / "output" / "scenario_run.json"),
    jsonl_output: Path = typer.Option(PROJECT_ROOT / ".local" / "output" / "scenario_run.jsonl"),
) -> None:
    raise typer.Exit(code=backend.cmd_run_scenario(scenario, prompt, population, index_dir, agent_limit, output, jsonl_output))


@app.command("aggregate")
def aggregate(
    run_result: Path = typer.Option(PROJECT_ROOT / ".local" / "output" / "scenario_run.json"),
    population: Path = typer.Option(PROJECT_ROOT / "agents" / "sample_profiles" / "tokyo_mvp_population.sample.json"),
    output: Path = typer.Option(PROJECT_ROOT / ".local" / "output" / "aggregated_output.json"),
    report: Path = typer.Option(PROJECT_ROOT / ".local" / "output" / "aggregation_report.md"),
) -> None:
    raise typer.Exit(code=backend.cmd_aggregate(run_result, population, output, report))


@app.command("estimate-demand")
def estimate_demand(
    aggregation: Path = typer.Option(PROJECT_ROOT / ".local" / "output" / "aggregated_output.json"),
    base_units: int = typer.Option(1000),
    output: Path = typer.Option(PROJECT_ROOT / ".local" / "output" / "demand_estimation.json"),
    report: Path = typer.Option(PROJECT_ROOT / ".local" / "output" / "demand_estimation_report.md"),
) -> None:
    raise typer.Exit(code=backend.cmd_estimate_demand(aggregation, base_units, output, report))


@app.command("evaluate")
def evaluate(
    population: Path = typer.Option(PROJECT_ROOT / "agents" / "sample_profiles" / "tokyo_mvp_population.sample.json"),
    aggregation: Path = typer.Option(PROJECT_ROOT / ".local" / "output" / "aggregated_output.json"),
    benchmark: Path = typer.Option(PROJECT_ROOT / "evaluation" / "benchmarks" / "tokyo_mvp_expected_distribution.json"),
    comparison_output: Optional[Path] = typer.Option(None),
    output: Path = typer.Option(PROJECT_ROOT / ".local" / "output" / "evaluation_record.json"),
    report: Path = typer.Option(PROJECT_ROOT / ".local" / "output" / "evaluation_report.md"),
) -> None:
    raise typer.Exit(code=backend.cmd_evaluate(population, aggregation, benchmark, comparison_output, output, report))


@app.command("run-example")
def run_example(
    config: Path = typer.Option(PROJECT_ROOT / "examples" / "tokyo-supermarket-launch" / "example_config.json"),
    prompt_kind: str = typer.Option("survey"),
    agent_limit: Optional[int] = typer.Option(None),
    base_units: Optional[int] = typer.Option(None),
    output_dir: Path = typer.Option(PROJECT_ROOT / ".local" / "examples" / "tokyo-supermarket-launch"),
) -> None:
    raise typer.Exit(code=backend.cmd_run_example(config, prompt_kind, agent_limit, base_units, output_dir))


def main(argv: list[str] | None = None) -> int:
    """Programmatic entrypoint used by the installed console script."""

    try:
        app(prog_name="ria", args=argv, standalone_mode=False)
        return 0
    except SystemExit as exc:
        return int(exc.code or 0)


if __name__ == "__main__":
    raise SystemExit(main())