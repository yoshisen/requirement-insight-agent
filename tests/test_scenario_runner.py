import json
from pathlib import Path

from simulations.runner import load_population_result, load_prompt_spec, load_scenario_definition, run_scenario, save_run_result


ROOT = Path(__file__).resolve().parent.parent


def test_run_scenario_survey_local(tmp_path: Path) -> None:
    scenario = load_scenario_definition(ROOT / "examples" / "tokyo-supermarket-launch" / "scenario.json")
    prompt_spec = load_prompt_spec(ROOT / "prompts" / "survey" / "supermarket-launch-survey-v1.json")
    population = load_population_result(ROOT / "agents" / "sample_profiles" / "tokyo_mvp_population.sample.json")

    result = run_scenario(
        scenario=scenario,
        prompt_spec=prompt_spec,
        population=population,
        index_dir=ROOT / ".local" / "index" / "sample",
        agent_limit=5,
    )

    assert result.response_count == 5
    assert len(result.responses) == 5
    assert all(1 <= response.purchase_intent <= 5 for response in result.responses)
    assert all(response.citations for response in result.responses)

    output_path = tmp_path / "scenario_run.json"
    jsonl_path = tmp_path / "scenario_run.jsonl"
    save_run_result(result, output_path, jsonl_path)

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    jsonl_lines = jsonl_path.read_text(encoding="utf-8").strip().splitlines()

    assert payload["response_count"] == 5
    assert len(jsonl_lines) == 5


def test_run_scenario_interview_multi_turn_sets_follow_up_summary() -> None:
    scenario = load_scenario_definition(ROOT / "examples" / "tokyo-supermarket-launch" / "scenario.json")
    prompt_spec = load_prompt_spec(ROOT / "prompts" / "interview" / "supermarket-launch-interview-v1.json")
    population = load_population_result(ROOT / "agents" / "sample_profiles" / "tokyo_mvp_population.sample.json")

    result = run_scenario(
        scenario=scenario,
        prompt_spec=prompt_spec,
        population=population,
        index_dir=ROOT / ".local" / "index" / "sample",
        agent_limit=2,
    )

    assert result.response_count == 2
    assert all(response.follow_up_summary for response in result.responses)