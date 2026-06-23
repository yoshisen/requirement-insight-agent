"""Scenario execution endpoints."""

from pathlib import Path

from fastapi import APIRouter

from api.schemas import ScenarioRunRequest
from requirement_insight_agent.project import PROJECT_ROOT
from simulations.runner import (
    load_population_result,
    load_prompt_spec,
    load_scenario_definition,
    run_scenario,
    save_run_result,
)


router = APIRouter(prefix="/scenario", tags=["scenario"])


@router.post("/run")
def run_scenario_endpoint(request: ScenarioRunRequest) -> dict:
    scenario = load_scenario_definition(PROJECT_ROOT / request.scenario_path)
    prompt_spec = load_prompt_spec(PROJECT_ROOT / request.prompt_path)
    population = load_population_result(PROJECT_ROOT / request.population_path)
    result = run_scenario(
        scenario=scenario,
        prompt_spec=prompt_spec,
        population=population,
        index_dir=PROJECT_ROOT / request.index_dir,
        agent_limit=request.agent_limit,
    )

    if request.output_path:
        jsonl_path = PROJECT_ROOT / request.jsonl_output if request.jsonl_output else None
        save_run_result(result, PROJECT_ROOT / request.output_path, jsonl_path)

    return result.model_dump(mode="json")