from starlette.testclient import TestClient

from main import app


client = TestClient(app)

def test_ingest_events():
    response = client.post("/events", json=[{
        "event_id": "uuid1",
        "occurred_at": "2026-01-16T00:00:00",
        "user_id": "user1",
        "event_type": "purchase",
        "properties": {}
    }])
    assert response.status_code == 200


def test_get_dau():
    response = client.get("/stats/dau?from=2026-01-01&to=2026-01-16")
    assert response.status_code == 200
    assert "dau" in response.json()



