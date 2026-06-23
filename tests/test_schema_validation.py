import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


ROOT = Path(__file__).resolve().parent.parent


SCHEMA_EXAMPLE_PAIRS = [
    ("schemas/agent.schema.json", "schemas/examples/agent.sample.json"),
    ("schemas/datasource.schema.json", "schemas/examples/datasource.sample.json"),
    ("schemas/scenario.schema.json", "schemas/examples/scenario.sample.json"),
    ("schemas/output.schema.json", "schemas/examples/output.sample.json"),
    ("schemas/evaluation.schema.json", "schemas/examples/evaluation.sample.json"),
]


def _load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


@pytest.mark.parametrize(("schema_path", "sample_path"), SCHEMA_EXAMPLE_PAIRS)
def test_schema_example_validates(schema_path: str, sample_path: str) -> None:
    schema = _load_json(schema_path)
    sample = _load_json(sample_path)

    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(sample)


def test_agent_schema_rejects_missing_metadata() -> None:
    schema = _load_json("schemas/agent.schema.json")
    sample = _load_json("schemas/examples/agent.sample.json")
    sample.pop("metadata")

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(sample)


def test_datasource_schema_rejects_invalid_quality_score() -> None:
    schema = _load_json("schemas/datasource.schema.json")
    sample = _load_json("schemas/examples/datasource.sample.json")
    sample["quality_score"] = 1.2

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(sample)


def test_scenario_schema_rejects_empty_region() -> None:
    schema = _load_json("schemas/scenario.schema.json")
    sample = _load_json("schemas/examples/scenario.sample.json")
    sample["region"] = []

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(sample)


def test_output_schema_requires_uncertainty_summary() -> None:
    schema = _load_json("schemas/output.schema.json")
    sample = _load_json("schemas/examples/output.sample.json")
    sample.pop("uncertainty_summary")

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(sample)


def test_evaluation_schema_rejects_empty_findings() -> None:
    schema = _load_json("schemas/evaluation.schema.json")
    sample = _load_json("schemas/examples/evaluation.sample.json")
    sample["findings"] = []

    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(sample)