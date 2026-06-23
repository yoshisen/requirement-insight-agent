"""Result retrieval endpoints for local output artifacts."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from api.schemas import FileResultResponse
from requirement_insight_agent.project import PROJECT_ROOT


router = APIRouter(prefix="/results", tags=["results"])


@router.get("/{artifact_name}", response_model=FileResultResponse)
def get_result_artifact(artifact_name: str) -> FileResultResponse:
    search_paths = [
        PROJECT_ROOT / ".local" / "output" / artifact_name,
        PROJECT_ROOT / ".local" / "examples" / "tokyo-supermarket-launch" / artifact_name,
    ]

    for path in search_paths:
        if path.exists():
            if path.suffix == ".json":
                content: object = json.loads(path.read_text(encoding="utf-8"))
                kind = "json"
            else:
                content = path.read_text(encoding="utf-8")
                kind = "text"
            return FileResultResponse(name=artifact_name, path=str(path), kind=kind, content=content)

    raise HTTPException(status_code=404, detail=f"Artifact not found: {artifact_name}")