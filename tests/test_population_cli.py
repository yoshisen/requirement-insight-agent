import json
from pathlib import Path

from requirement_insight_agent.cli import main


ROOT = Path(__file__).resolve().parent.parent


def test_cli_build_population_generates_output(tmp_path: Path) -> None:
    output_path = tmp_path / "population.sample.json"

    exit_code = main(
        [
            "build-population",
            "--config",
            str(ROOT / "configs" / "populations" / "tokyo_mvp_population.json"),
            "--sample-size",
            "6",
            "--category",
            "frozen_food",
            "--output",
            str(output_path),
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert payload["sample_size"] == 6
    assert len(payload["records"]) == 6