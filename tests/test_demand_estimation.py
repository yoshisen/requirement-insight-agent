from pathlib import Path

from agents.builders.population_builder import build_population, load_population_config
from rag.indexing.build import build_index_from_processed
from simulations.aggregation import aggregate_run
from simulations.demand.estimator import DemandEstimationInput, build_demand_estimation
from simulations.inventory.suggestion import build_inventory_suggestion
from simulations.runner import load_prompt_spec, load_scenario_definition, run_scenario


ROOT = Path(__file__).resolve().parent.parent


def test_build_demand_estimation_outputs_required_ranges(tmp_path: Path) -> None:
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

    estimation = build_demand_estimation(DemandEstimationInput(aggregation_output=aggregated))

    assert set(estimation.ranges) == {"conservative", "base", "optimistic"}
    assert estimation.ranges["conservative"].lower <= estimation.ranges["conservative"].upper
    assert estimation.assumptions
    assert estimation.risk_factors
    assert estimation.segment_sensitivity


def test_inventory_suggestion_uses_estimation_ranges(tmp_path: Path) -> None:
    index_dir = tmp_path / "index"
    build_index_from_processed(
        processed_path=ROOT / "data" / "processed" / "normalized_records.json",
        output_dir=index_dir,
    )
    config = load_population_config(ROOT / "configs" / "populations" / "tokyo_mvp_population.json")
    population = build_population(config, sample_size=5, category="frozen_food")
    scenario = load_scenario_definition(ROOT / "examples" / "tokyo-supermarket-launch" / "scenario.json")
    prompt_spec = load_prompt_spec(ROOT / "prompts" / "survey" / "supermarket-launch-survey-v1.json")
    run_result = run_scenario(
        scenario=scenario,
        prompt_spec=prompt_spec,
        population=population,
        index_dir=index_dir,
        agent_limit=5,
    )
    aggregated = aggregate_run(run_result=run_result, population=population)
    estimation = build_demand_estimation(DemandEstimationInput(aggregation_output=aggregated))

    inventory = build_inventory_suggestion(estimation)

    assert inventory["base"]["suggested_min_stock"] <= inventory["base"]["suggested_max_stock"]