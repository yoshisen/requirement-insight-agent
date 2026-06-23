"""Minimal FastAPI app for Requirement Insight Agent."""

from fastapi import FastAPI

from api.routes.example import router as example_router
from api.routes.health import router as health_router
from api.routes.population import router as population_router
from api.routes.results import router as results_router
from api.routes.scenario import router as scenario_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Requirement Insight Agent API",
        version="0.1.0",
        description="Minimal API for running the Requirement Insight Agent MVP pipeline.",
    )
    app.include_router(health_router)
    app.include_router(population_router)
    app.include_router(scenario_router)
    app.include_router(example_router)
    app.include_router(results_router)
    return app


app = create_app()