"""Population build endpoints."""

from pathlib import Path

from fastapi import APIRouter

from agents.builders.population_builder import build_population, load_population_config, save_population_result
from api.schemas import PopulationBuildRequest
from requirement_insight_agent.project import PROJECT_ROOT


router = APIRouter(prefix="/population", tags=["population"])


@router.post("/build")
def build_population_endpoint(request: PopulationBuildRequest) -> dict:
    config = load_population_config(PROJECT_ROOT / request.config_path)
    result = build_population(config, sample_size=request.sample_size, category=request.category)

    if request.output_path:
        save_population_result(result, PROJECT_ROOT / request.output_path)

    return result.model_dump(mode="json")