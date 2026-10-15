from fastapi.testclient import TestClient
from main import app

client = TestClient(app, headers={"x-api-key": "dev-secret-key"})
unauthenticated_client = TestClient(app)

def test_get_alerts_without_api_key():
    r = unauthenticated_client.get("/alerts")
    assert r.status_code == 401

def test_get_alerts_with_wrong_api_key():
    r = client.get("/alerts", headers={"x-api-key": "wrong-key"})
    assert r.status_code == 401

def test_get_alerts():
    r = client.get("/alerts")
    assert r.status_code == 200

def test_create_alert_invalid_level():
    r = client.post("/alerts", json={"title": "x", "level": "urgent"})
    assert r.status_code == 422

def test_create_alert_ok():
    r = client.post("/alerts", json={"title": "x", "level": "info"})
    assert r.status_code == 201
    assert "id" in r.json()

def test_create_alert_missing_title():
    r = client.post("/alerts", json={"level": "info"})
    assert r.status_code == 422

def test_get_alert_by_id_ok():
    r = client.get("/alerts/by-id/1")
    assert r.status_code == 200
    assert r.json()["title"] == "CPU 高"

def test_get_alert_by_id_404():
    r = client.get("/alerts/by-id/999")
    assert r.status_code == 404

def test_get_alerts_by_level():
    r = client.get("/alerts/warning?limit=2")
    assert r.status_code == 200
    assert len(r.json()) <= 2

def test_get_alerts_invalid_limit():
    r = client.get("/alerts/warning?limit=abc")
    assert r.status_code == 422

def test_pagination():
    r = client.get("/alerts?page=1&page_size=2")
    assert r.status_code == 200
    data = r.json()
    assert "total" in data
    assert len(data["items"]) == 2

def test_delete_alert():
    created = client.post("/alerts", json={"title": "delete me", "level": "info"})
    assert created.status_code == 201
    alert_id = created.json()["id"]

    deleted = client.delete(f"/alerts/{alert_id}")
    assert deleted.status_code == 201

    missing = client.get(f"/alerts/by-id/{alert_id}")
    assert missing.status_code == 404

