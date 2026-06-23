from fastapi.testclient import TestClient

from api.app import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_example_endpoint_runs() -> None:
    response = client.post(
        "/examples/tokyo-supermarket-launch/run",
        json={
            "config_path": "examples/tokyo-supermarket-launch/example_config.json",
            "prompt_kind": "survey",
            "agent_limit": 3,
            "base_units": 800,
            "output_dir": ".local/examples/api-test",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "aggregated_output" in payload
    assert "demand_output" in payload