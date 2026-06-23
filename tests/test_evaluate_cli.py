from pathlib import Path

from agents.builders.population_builder import build_population, load_population_config, save_population_result
from evaluation.calibration import save_evaluation_record
from rag.indexing.build import build_index_from_processed
from requirement_insight_agent.cli import main
from simulations.aggregation import aggregate_run, save_aggregated_output
from simulations.runner import load_prompt_spec, load_scenario_definition, run_scenario


ROOT = Path(__file__).resolve().parent.parent


def test_cli_evaluate_generates_json_and_report(tmp_path: Path) -> None:
    index_dir = tmp_path / "index"
    build_index_from_processed(processed_path=ROOT / "data" / "processed" / "normalized_records.json", output_dir=index_dir)
    config = load_population_config(ROOT / "configs" / "populations" / "tokyo_mvp_population.json")
    population = build_population(config, sample_size=6, category="frozen_food")
    population_path = tmp_path / "population.json"
    save_population_result(population, population_path)
    scenario = load_scenario_definition(ROOT / "examples" / "tokyo-supermarket-launch" / "scenario.json")
    prompt_spec = load_prompt_spec(ROOT / "prompts" / "survey" / "supermarket-launch-survey-v1.json")
    run_result = run_scenario(scenario=scenario, prompt_spec=prompt_spec, population=population, index_dir=index_dir, agent_limit=6)
    aggregated = aggregate_run(run_result=run_result, population=population)
    aggregation_path = tmp_path / "aggregated.json"
    save_aggregated_output(aggregated, aggregation_path)

    output_path = tmp_path / "evaluation_record.json"
    report_path = tmp_path / "evaluation_report.md"
    exit_code = main([
        "evaluate",
        "--population", str(population_path),
        "--aggregation", str(aggregation_path),
        "--benchmark", str(ROOT / "evaluation" / "benchmarks" / "tokyo_mvp_expected_distribution.json"),
        "--output", str(output_path),
        "--report", str(report_path),
    ])

    assert exit_code == 0
    assert output_path.exists()
    assert report_path.exists()


def test_cli_run_example_generates_artifacts(tmp_path: Path) -> None:
    exit_code = main([
        "run-example",
        "--config", str(ROOT / "examples" / "tokyo-supermarket-launch" / "example_config.json"),
        "--output-dir", str(tmp_path / "example-output"),
        "--agent-limit", "4",
        "--base-units", "800",
    ])

    assert exit_code == 0
    assert (tmp_path / "example-output" / "evaluation_record.json").exists()
    assert (tmp_path / "example-output" / "demand_estimation.json").exists()