"""CLI-oriented scenario runner for survey and interview execution."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from agents.models import SyntheticConsumerAgent
from agents.orchestration.executor import execute_prompt_for_agent
from agents.population import PopulationBuildResult
from rag.grounding.builder import build_grounding_context
from rag.retrieval.search import RetrievalQuery, retrieve_chunks
from requirement_insight_agent.core.config import AppConfig, load_settings
from requirement_insight_agent.core.providers.factory import create_provider_stack
from simulations.models import PromptSpec, ScenarioDefinition, ScenarioRunResult


def load_prompt_spec(path: Path) -> PromptSpec:
    """Load a prompt specification JSON file."""

    return PromptSpec.model_validate(json.loads(path.read_text(encoding="utf-8")))


def load_scenario_definition(path: Path) -> ScenarioDefinition:
    """Load a scenario definition JSON file."""

    return ScenarioDefinition.model_validate(json.loads(path.read_text(encoding="utf-8")))


def load_population_result(path: Path) -> PopulationBuildResult:
    """Load a generated synthetic population JSON file."""

    return PopulationBuildResult.model_validate(json.loads(path.read_text(encoding="utf-8")))


def run_scenario(
    *,
    scenario: ScenarioDefinition,
    prompt_spec: PromptSpec,
    population: PopulationBuildResult,
    index_dir: Path,
    agent_limit: int,
    settings: AppConfig | None = None,
) -> ScenarioRunResult:
    """Run one survey or interview spec across a subset of synthetic agents."""

    settings = settings or load_settings()
    provider_stack = create_provider_stack(settings)
    selected_records = population.records[:agent_limit]
    responses = []

    for record in selected_records:
        agent = record.agent if isinstance(record.agent, SyntheticConsumerAgent) else SyntheticConsumerAgent.model_validate(record.agent)
        retrieval_query = _build_retrieval_query(agent=agent, scenario=scenario, prompt_spec=prompt_spec)
        retrieval_result = retrieve_chunks(index_dir=index_dir, query=retrieval_query, settings=settings)
        if not retrieval_result.retrieved_chunks and scenario.region:
            retrieval_query = retrieval_query.model_copy(
                update={"region_filters": scenario.region}
            )
            retrieval_result = retrieve_chunks(index_dir=index_dir, query=retrieval_query, settings=settings)
        grounding_context = build_grounding_context(retrieval_query, retrieval_result.retrieved_chunks)
        response = execute_prompt_for_agent(
            agent=agent,
            scenario=scenario,
            prompt_spec=prompt_spec,
            grounding_context=grounding_context,
            provider_stack=provider_stack,
            max_retries=settings.max_retries,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
        )
        responses.append(response)

    return ScenarioRunResult(
        run_id=f"run-{uuid.uuid4().hex[:8]}",
        scenario_id=scenario.scenario_id,
        prompt_spec_id=prompt_spec.prompt_spec_id,
        mode=prompt_spec.mode,
        response_count=len(responses),
        responses=responses,
        metadata={
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "agent_limit": agent_limit,
            "population_id": population.population_id,
        },
    )


def save_run_result(result: ScenarioRunResult, output_path: Path, jsonl_path: Path | None = None) -> Path:
    """Persist a scenario run result bundle and optional JSONL records."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")

    if jsonl_path is not None:
        jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        with jsonl_path.open("w", encoding="utf-8") as handle:
            for response in result.responses:
                handle.write(json.dumps(response.model_dump(mode="json"), ensure_ascii=False) + "\n")

    return output_path


def _build_retrieval_query(
    *,
    agent: SyntheticConsumerAgent,
    scenario: ScenarioDefinition,
    prompt_spec: PromptSpec,
) -> RetrievalQuery:
    category_filters = [category for category in scenario.category if category != "supermarket"]
    if not category_filters and agent.category_preferences:
        category_filters = [agent.category_preferences[0]]

    query_text = " ".join(
        [
            scenario.product_or_service.name,
            scenario.product_or_service.description,
            scenario.business_question,
            " ".join(agent.category_preferences[:2]),
            agent.region,
            prompt_spec.mode,
        ]
    )

    return RetrievalQuery(
        query_text=query_text,
        top_k=3,
        min_score=0.05,
        region_filters=[agent.region],
        category_filters=category_filters,
        scenario_id=scenario.scenario_id,
        agent_id=agent.agent_id,
    )