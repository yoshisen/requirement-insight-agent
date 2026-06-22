"""Project-level path helpers used by the MVP scaffold."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SCAFFOLD_PATHS = {
    "package": PROJECT_ROOT / "requirement_insight_agent",
    "docs": PROJECT_ROOT / "docs",
    "configs": PROJECT_ROOT / "configs",
    "schemas": PROJECT_ROOT / "schemas",
    "data": PROJECT_ROOT / "data",
    "data_raw": PROJECT_ROOT / "data" / "raw",
    "data_processed": PROJECT_ROOT / "data" / "processed",
    "data_sample": PROJECT_ROOT / "data" / "sample",
    "ingestion": PROJECT_ROOT / "ingestion",
    "rag": PROJECT_ROOT / "rag",
    "agents": PROJECT_ROOT / "agents",
    "prompts": PROJECT_ROOT / "prompts",
    "simulations": PROJECT_ROOT / "simulations",
    "evaluation": PROJECT_ROOT / "evaluation",
    "api": PROJECT_ROOT / "api",
    "examples": PROJECT_ROOT / "examples",
    "tests": PROJECT_ROOT / "tests",
}


def scaffold_status() -> dict[str, bool]:
    """Return whether each expected top-level path is present."""

    return {name: path.exists() for name, path in SCAFFOLD_PATHS.items()}