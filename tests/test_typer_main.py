from typer.testing import CliRunner

from requirement_insight_agent.main import app


runner = CliRunner()


def test_typer_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "run-example" in result.output


def test_typer_status() -> None:
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "project_root" in result.output