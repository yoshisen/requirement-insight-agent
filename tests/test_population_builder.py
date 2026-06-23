import json
from pathlib import Path

from agents.builders.population_builder import build_population, load_population_config, save_population_result
from agents.models import SyntheticConsumerAgent


ROOT = Path(__file__).resolve().parent.parent


def test_population_builder_generates_expected_count() -> None:
    config = load_population_config(ROOT / "configs" / "populations" / "tokyo_mvp_population.json")

    result = build_population(config, sample_size=24, category="frozen_food")

    assert result.sample_size == 24
    assert len(result.records) == 24
    assert all(record.agent.metadata.population_config_id == "tokyo-mvp-v1" for record in result.records)


def test_population_builder_outputs_valid_agents() -> None:
    config = load_population_config(ROOT / "configs" / "populations" / "tokyo_mvp_population.json")
    result = build_population(config, sample_size=8, category="frozen_food")

    for record in result.records:
        validated = SyntheticConsumerAgent.model_validate(record.agent.model_dump(mode="json"))
        assert "frozen_food" in validated.category_preferences
        assert record.raw_traits.requested_category == "frozen_food"
        assert record.explanation_trace


def test_population_builder_writes_json_output(tmp_path: Path) -> None:
    config = load_population_config(ROOT / "configs" / "populations" / "tokyo_mvp_population.json")
    result = build_population(config, sample_size=5)

    output_path = tmp_path / "population.json"
    save_population_result(result, output_path)
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert payload["sample_size"] == 5
    assert len(payload["records"]) == 5