import json
from pathlib import Path

from agents.builders.population_builder import build_population, load_population_config, save_population_result
from rag.indexing.build import build_index_from_processed
from requirement_insight_agent.cli import main
from simulations.runner import load_prompt_spec, load_scenario_definition, run_scenario, save_run_result


ROOT = Path(__file__).resolve().parent.parent


def test_cli_aggregate_generates_json_and_report(tmp_path: Path) -> None:
    index_dir = tmp_path / "index"
    build_index_from_processed(
        processed_path=ROOT / "data" / "processed" / "normalized_records.json",
        output_dir=index_dir,
    )
    config = load_population_config(ROOT / "configs" / "populations" / "tokyo_mvp_population.json")
    population = build_population(config, sample_size=5, category="frozen_food")
    population_path = tmp_path / "population.json"
    save_population_result(population, population_path)

    scenario = load_scenario_definition(ROOT / "examples" / "tokyo-supermarket-launch" / "scenario.json")
    prompt_spec = load_prompt_spec(ROOT / "prompts" / "survey" / "supermarket-launch-survey-v1.json")
    run_result = run_scenario(
        scenario=scenario,
        prompt_spec=prompt_spec,
        population=population,
        index_dir=index_dir,
        agent_limit=5,
    )
    run_result_path = tmp_path / "scenario_run.json"
    save_run_result(run_result, run_result_path)

    output_path = tmp_path / "aggregated_output.json"
    report_path = tmp_path / "aggregation_report.md"
    exit_code = main(
        [
            "aggregate",
            "--run-result",
            str(run_result_path),
            "--population",
            str(population_path),
            "--output",
            str(output_path),
            "--report",
            str(report_path),
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    report_text = report_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert payload["summary"]["overall_takeaway"]
    assert "Overall Summary" in report_text