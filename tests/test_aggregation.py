import json
from pathlib import Path

from agents.builders.population_builder import build_population, load_population_config
from rag.indexing.build import build_index_from_processed
from simulations.aggregation import aggregate_run, save_aggregated_output
from simulations.reporting import build_markdown_report, save_markdown_report
from simulations.runner import load_prompt_spec, load_scenario_definition, run_scenario


ROOT = Path(__file__).resolve().parent.parent


def test_aggregate_run_builds_machine_readable_output(tmp_path: Path) -> None:
    index_dir = tmp_path / "index"
    build_index_from_processed(
        processed_path=ROOT / "data" / "processed" / "normalized_records.json",
        output_dir=index_dir,
    )
    config = load_population_config(ROOT / "configs" / "populations" / "tokyo_mvp_population.json")
    population = build_population(config, sample_size=6, category="frozen_food")
    scenario = load_scenario_definition(ROOT / "examples" / "tokyo-supermarket-launch" / "scenario.json")
    prompt_spec = load_prompt_spec(ROOT / "prompts" / "survey" / "supermarket-launch-survey-v1.json")
    run_result = run_scenario(
        scenario=scenario,
        prompt_spec=prompt_spec,
        population=population,
        index_dir=index_dir,
        agent_limit=6,
    )

    aggregated = aggregate_run(run_result=run_result, population=population)

    assert aggregated.scenario_id == scenario.scenario_id
    assert aggregated.segment_summaries
    assert aggregated.summary.top_reasons
    assert aggregated.citation_summary
    assert aggregated.explanation_trace

    output_path = tmp_path / "aggregated_output.json"
    report_path = tmp_path / "aggregation_report.md"
    save_aggregated_output(aggregated, output_path)
    save_markdown_report(build_markdown_report(aggregated), report_path)

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    report_text = report_path.read_text(encoding="utf-8")

    assert payload["scenario_id"] == scenario.scenario_id
    assert "Overall Summary" in report_text
    assert "structured simulation summary" in report_text