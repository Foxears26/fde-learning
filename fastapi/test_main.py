from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_alerts():
    r = client.get("/alerts")
    assert r.status_code == 200

def test_create_alert_invalid_level():
    r = client.post("/alerts", json={"title": "x", "level": "urgent"})
    assert r.status_code == 422

def test_create_alert_ok():
    r = client.post("/alerts", json={"title": "x", "level": "info"})
    assert r.status_code == 201

def test_create_alert_missing_title():
    r = client.post("/alerts", json={"level": "info"})
    assert r.status_code == 422

def test_get_alert_by_id_ok():
    r = client.get("/alerts/by-id/1")
    assert r.status_code == 200

def test_get_alert_by_id_404():
    r = client.get("/alerts/by-id/999")
    assert r.status_code == 404

