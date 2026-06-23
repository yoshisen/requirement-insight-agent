import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from agents.models import SyntheticConsumerAgent
from evaluation.models import EvaluationRecord
from rag.models import CitationTrace, DataSourceMetadata
from simulations.models import AggregatedOutput, DemandRange, ScenarioDefinition


ROOT = Path(__file__).resolve().parent.parent


def _load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def test_domain_model_docstrings_exist() -> None:
    assert SyntheticConsumerAgent.__doc__
    assert DataSourceMetadata.__doc__
    assert CitationTrace.__doc__
    assert ScenarioDefinition.__doc__
    assert AggregatedOutput.__doc__
    assert EvaluationRecord.__doc__


def test_agent_model_accepts_schema_example() -> None:
    agent = SyntheticConsumerAgent.model_validate(_load_json("schemas/examples/agent.sample.json"))

    assert agent.agent_id == "tokyo-agent-0001"


def test_datasource_model_accepts_schema_example() -> None:
    datasource = DataSourceMetadata.model_validate(
        _load_json("schemas/examples/datasource.sample.json")
    )

    assert datasource.license_type == "internal"


def test_scenario_model_accepts_schema_example() -> None:
    scenario = ScenarioDefinition.model_validate(_load_json("schemas/examples/scenario.sample.json"))

    assert scenario.target_agents.sample_size == 20


def test_output_model_accepts_schema_example() -> None:
    output = AggregatedOutput.model_validate(_load_json("schemas/examples/output.sample.json"))

    assert output.uncertainty_summary.overall_uncertainty == "medium"


def test_evaluation_model_accepts_schema_example() -> None:
    record = EvaluationRecord.model_validate(_load_json("schemas/examples/evaluation.sample.json"))

    assert record.target_type == "population"


def test_demand_range_rejects_reversed_bounds() -> None:
    with pytest.raises(ValidationError):
        DemandRange(lower=100, upper=50, unit="units_per_period")