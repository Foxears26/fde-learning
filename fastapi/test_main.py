from fastapi.testclient import TestClient
import pytest
from main import app

#client = TestClient(app, headers={"x-api-key": "dev-secret-key"}) 
#unauthenticated_client = TestClient(app)
#upgrade to pytest fixture
@pytest.fixture
def client():
    from routers.alerts import alerts
    alerts.clear()
    alerts.extend([
        {"id": 1, "level": "warning", "title": "CPU 高"},
        {"id": 2, "level": "critical", "title": "磁盘满"},
        {"id": 3, "level": "warning", "title": "内存高"},
        {"id": 4, "level": "info", "title": "备份完成"},
    ])
    return TestClient(app, headers={"x-api-key": "dev-secret-key"})

@pytest.fixture
def unauthenticated_client():
    return TestClient(app) 

#add parametrize test
@pytest.mark.parametrize("bad_level", ["urgent", "", "WARNING", "123"])
def test_create_alert_bad_levels(client, bad_level):
    r = client.post("/alerts", json={"title": "x", "level": bad_level})
    assert r.status_code == 422

@pytest.mark.parametrize("bad_body", [
    {},
    {"level": "warning"},
    {"title": "x"},
    {"title": "x", "level": "urgent"},
])
def test_create_alert_bad_bodies(client, bad_body):
    r = client.post("/alerts", json=bad_body)
    assert r.status_code == 422

@pytest.mark.parametrize("level", ["info", "warning", "critical"])
def test_get_alerts_by_level_param(client, level):
    r = client.get(f"/alerts/{level}")
    assert r.status_code == 200
    assert all(a["level"] == level for a in r.json())

@pytest.mark.parametrize("page,page_size,expected_len", [(1, 2, 2), (2, 2, 2), (1, 10, 4), (3, 2, 0)])
def test_pagination_param(client, page, page_size, expected_len):
    r = client.get(f"/alerts?page={page}&page_size={page_size}")
    assert r.status_code == 200
    assert len(r.json()["items"]) == expected_len


def test_get_alerts_without_api_key(unauthenticated_client):
    r = unauthenticated_client.get("/alerts")
    assert r.status_code == 401

def test_get_alerts_with_wrong_api_key(client):
    r = client.get("/alerts", headers={"x-api-key": "wrong-key"})
    assert r.status_code == 401

def test_get_alerts(client):
    r = client.get("/alerts")
    assert r.status_code == 200

def test_create_alert_invalid_level(client):
    r = client.post("/alerts", json={"title": "x", "level": "urgent"})
    assert r.status_code == 422

def test_create_alert_ok(client):
    r = client.post("/alerts", json={"title": "x", "level": "info"})
    assert r.status_code == 201
    assert "id" in r.json()

def test_create_alert_missing_title(client):
    r = client.post("/alerts", json={"level": "info"})
    assert r.status_code == 422

def test_get_alert_by_id_ok(client):
    r = client.get("/alerts/by-id/1")
    assert r.status_code == 200
    assert r.json()["title"] == "CPU 高"

def test_get_alert_by_id_404(client):
    r = client.get("/alerts/by-id/999")
    assert r.status_code == 404

def test_get_alerts_by_level(client):
    r = client.get("/alerts/warning?limit=2")
    assert r.status_code == 200
    assert len(r.json()) <= 2

def test_get_alerts_invalid_limit(client):
    r = client.get("/alerts/warning?limit=abc")
    assert r.status_code == 422

def test_pagination(client):
    r = client.get("/alerts?page=1&page_size=2")
    assert r.status_code == 200
    data = r.json()
    assert "total" in data
    assert len(data["items"]) == 2

def test_delete_alert(client):
    created = client.post("/alerts", json={"title": "delete me", "level": "info"})
    assert created.status_code == 201
    alert_id = created.json()["id"]

    deleted = client.delete(f"/alerts/{alert_id}")
    assert deleted.status_code == 201

    missing = client.get(f"/alerts/by-id/{alert_id}")
    assert missing.status_code == 404

