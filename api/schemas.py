"""Request and response models for the minimal FastAPI layer."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PopulationBuildRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    config_path: str = "configs/populations/tokyo_mvp_population.json"
    sample_size: int | None = Field(default=None, ge=1)
    category: str | None = None
    output_path: str | None = None


class ScenarioRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_path: str = "examples/tokyo-supermarket-launch/scenario.json"
    prompt_path: str = "prompts/survey/supermarket-launch-survey-v1.json"
    population_path: str = "agents/sample_profiles/tokyo_mvp_population.sample.json"
    index_dir: str = ".local/index/sample"
    agent_limit: int = Field(default=5, ge=1)
    output_path: str | None = None
    jsonl_output: str | None = None


class ExampleRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    config_path: str = "examples/tokyo-supermarket-launch/example_config.json"
    prompt_kind: str = "survey"
    agent_limit: int | None = Field(default=None, ge=1)
    base_units: int | None = Field(default=None, ge=1)
    output_dir: str = ".local/examples/tokyo-supermarket-launch"


class FileResultResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    path: str
    kind: str
    content: object