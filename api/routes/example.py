"""Example workflow endpoints."""

from fastapi import APIRouter

from api.schemas import ExampleRunRequest
from requirement_insight_agent.project import PROJECT_ROOT
from requirement_insight_agent.workflows import load_example_config, run_example_workflow


router = APIRouter(prefix="/examples", tags=["examples"])


@router.post("/tokyo-supermarket-launch/run")
def run_tokyo_supermarket_example(request: ExampleRunRequest) -> dict:
    config = load_example_config(PROJECT_ROOT / request.config_path)
    artifacts = run_example_workflow(
        config=config,
        output_dir=PROJECT_ROOT / request.output_dir,
        prompt_kind=request.prompt_kind,
        agent_limit=request.agent_limit,
        base_units=request.base_units,
    )
    return artifacts.model_dump(mode="json")