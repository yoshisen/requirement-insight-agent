from requirement_insight_agent import __version__
from requirement_insight_agent.project import scaffold_status


def test_version_is_defined() -> None:
    assert __version__ == "0.1.0"


def test_scaffold_status_returns_mapping() -> None:
    status = scaffold_status()

    assert isinstance(status, dict)
    assert "docs" in status
    assert "tests" in status