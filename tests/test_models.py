from datetime import datetime, timezone
from importlib import import_module

import pytest
from pydantic import ValidationError


def _models_module():
    module_name = "requirement_insight_agent" + ".models"
    return import_module(module_name)


def test_synthetic_agent_accepts_mvp_payload() -> None:
    models = _models_module()

    agent = models.SyntheticConsumerAgent(
        agent_id="tokyo-agent-0001",
        region="tokyo-metropolitan",
        age_band="30s",
        household_composition="single",
        income_band="middle",
        channel_preference="hybrid",
        price_sensitivity="medium",
        category_preferences=["frozen_food", "healthy_food"],
        uncertainty_profile=models.UncertaintyProfile(
            profile_confidence="medium",
            preference_uncertainty="medium",
            category_familiarity="high",
        ),
        response_style=models.ResponseStyle(
            verbosity="medium",
            directness="medium",
            confidence_expression="cautious",
        ),
        metadata=models.AgentMetadata(
            generated_at=datetime(2026, 6, 22, 10, 0, tzinfo=timezone.utc),
            generator_version="0.1.0",
            population_config_id="tokyo-mvp-v1",
            seed=42,
        ),
    )

    assert agent.agent_id == "tokyo-agent-0001"


def test_synthetic_agent_requires_non_empty_categories() -> None:
    models = _models_module()

    with pytest.raises(ValidationError):
        models.SyntheticConsumerAgent(
            agent_id="tokyo-agent-0002",
            region="tokyo-metropolitan",
            age_band="30s",
            household_composition="single",
            income_band="middle",
            channel_preference="hybrid",
            price_sensitivity="medium",
            category_preferences=[],
            uncertainty_profile=models.UncertaintyProfile(
                profile_confidence="medium",
                preference_uncertainty="medium",
                category_familiarity="high",
            ),
            response_style=models.ResponseStyle(
                verbosity="medium",
                directness="medium",
                confidence_expression="cautious",
            ),
            metadata=models.AgentMetadata(
                generated_at=datetime(2026, 6, 22, 10, 0, tzinfo=timezone.utc),
                generator_version="0.1.0",
                population_config_id="tokyo-mvp-v1",
                seed=42,
            ),
        )


def test_datasource_metadata_validates_quality_score() -> None:
    models = _models_module()

    datasource = models.DatasourceMetadata(
        datasource_id="sample-market-note-001",
        source_name="Tokyo Frozen Food Market Notes",
        source_type="market_notes",
        license_type="internal",
        allowed_use=["research", "prototype"],
        retrieved_at=datetime(2026, 6, 22, 10, 0, tzinfo=timezone.utc),
        coverage_region=["tokyo-metropolitan"],
        quality_score=0.7,
        provenance=models.Provenance(
            collected_by="project-team",
            collected_method="manual_import",
            notes="sample data for MVP",
        ),
    )

    assert datasource.quality_score == 0.7


def test_scenario_definition_requires_lists() -> None:
    models = _models_module()

    scenario = models.ScenarioDefinition(
        scenario_id="tokyo-supermarket-launch",
        title="Tokyo supermarket frozen meal launch",
        region=["tokyo-metropolitan"],
        category=["supermarket", "frozen_food"],
        business_question="Should we launch a high-protein frozen side dish line?",
        target_agents=models.TargetAgents(population_id="tokyo-mvp-v1", sample_size=50),
        product_or_service=models.ProductOrService(
            name="Protein Frozen Deli",
            description="High-protein low-sugar frozen deli series.",
            price_options=[398, 498, 598],
            positioning=["healthy", "quick_meal"],
        ),
        evaluation_dimensions=["purchase_intent", "price_sensitivity"],
        assumptions=["Tokyo metro supermarket context"],
        metadata=models.ScenarioMetadata(
            created_at=datetime(2026, 6, 22, 10, 0, tzinfo=timezone.utc),
            created_by="test-suite",
            version="0.1.0",
        ),
    )

    assert scenario.scenario_id == "tokyo-supermarket-launch"