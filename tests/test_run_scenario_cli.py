import json
from pathlib import Path

from requirement_insight_agent.cli import main


ROOT = Path(__file__).resolve().parent.parent


def test_cli_run_scenario_generates_json_and_jsonl(tmp_path: Path) -> None:
    output_path = tmp_path / "scenario_run.json"
    jsonl_path = tmp_path / "scenario_run.jsonl"

    exit_code = main(
        [
            "run-scenario",
            "--scenario",
            str(ROOT / "examples" / "tokyo-supermarket-launch" / "scenario.json"),
            "--prompt",
            str(ROOT / "prompts" / "survey" / "supermarket-launch-survey-v1.json"),
            "--population",
            str(ROOT / "agents" / "sample_profiles" / "tokyo_mvp_population.sample.json"),
            "--index-dir",
            str(ROOT / ".local" / "index" / "sample"),
            "--agent-limit",
            "4",
            "--output",
            str(output_path),
            "--jsonl-output",
            str(jsonl_path),
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    lines = jsonl_path.read_text(encoding="utf-8").strip().splitlines()

    assert exit_code == 0
    assert payload["response_count"] == 4
    assert len(lines) == 4