from pathlib import Path

from agents.builders.population_builder import build_population, load_population_config
from evaluation.calibration import build_evaluation_markdown_report, evaluate_artifacts
from rag.indexing.build import build_index_from_processed
from simulations.aggregation import aggregate_run
from simulations.runner import load_prompt_spec, load_scenario_definition, run_scenario


ROOT = Path(__file__).resolve().parent.parent


def test_evaluation_builds_record_from_population_and_aggregate(tmp_path: Path) -> None:
    index_dir = tmp_path / "index"
    build_index_from_processed(
        processed_path=ROOT / "data" / "processed" / "normalized_records.json",
        output_dir=index_dir,
    )
    config = load_population_config(ROOT / "configs" / "populations" / "tokyo_mvp_population.json")
    population = build_population(config, sample_size=8, category="frozen_food")
    scenario = load_scenario_definition(ROOT / "examples" / "tokyo-supermarket-launch" / "scenario.json")
    prompt_spec = load_prompt_spec(ROOT / "prompts" / "survey" / "supermarket-launch-survey-v1.json")
    run_result = run_scenario(
        scenario=scenario,
        prompt_spec=prompt_spec,
        population=population,
        index_dir=index_dir,
        agent_limit=8,
    )
    aggregated = aggregate_run(run_result=run_result, population=population)

    record = evaluate_artifacts(
        population=population,
        aggregated=aggregated,
        benchmark_path=ROOT / "evaluation" / "benchmarks" / "tokyo_mvp_expected_distribution.json",
    )

    assert record.metrics.representativeness_score is not None
    assert record.metrics.stability_score is not None
    assert record.findings
    assert build_evaluation_markdown_report(record)