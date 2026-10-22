import os

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from database import DATABASE_URL, get_db
from db_models import Alert, Base
from main import app

@pytest.fixture(scope="session")
def test_engine():
    url = make_url(os.getenv("TEST_DATABASE_URL", DATABASE_URL)).set(database="alertsdb_test")
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(autouse=True)
def reset_database(test_engine):
    seeds = [
        {"id": 1, "level": "warning", "title": "CPU 高"},
        {"id": 2, "level": "critical", "title": "磁盘满"},
        {"id": 3, "level": "warning", "title": "内存高"},
        {"id": 4, "level": "info", "title": "备份完成"},
    ]
    with Session(test_engine) as db:
        db.execute(text("TRUNCATE TABLE alerts RESTART IDENTITY"))
        db.add_all([Alert(title=seed["title"], level=seed["level"]) for seed in seeds])
        db.commit()

    def override_get_db():
        with Session(test_engine) as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_db, None)
        with Session(test_engine) as db:
            db.execute(text("TRUNCATE TABLE alerts RESTART IDENTITY"))
            db.commit()


@pytest.fixture
def client():
    with TestClient(app, headers={"x-api-key": "dev-secret-key"}) as client:
        yield client

@pytest.fixture
def unauthenticated_client():
    with TestClient(app) as client:
        yield client

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
def test_pagination_first_page_returns_first_items(client):
    r = client.get("/alerts?page=1&page_size=2")
    assert [item["id"] for item in r.json()["items"]] == [1, 2]



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



def test_update_alert_persists(client, test_engine):
    response = client.put("/alerts/1", json={"title": "updated", "level": "info"})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "title": "updated", "level": "info"}
    with Session(test_engine) as db:
        stored = db.get(Alert, 1)
        assert (stored.title, stored.level) == ("updated", "info")
    assert client.get("/alerts/by-id/1").json() == response.json()


@pytest.mark.parametrize("method", ["put", "delete"])
def test_write_missing_alert(client, method):
    kwargs = {"json": {"title": "x", "level": "info"}} if method == "put" else {}
    response = getattr(client, method)("/alerts/999", **kwargs)
    assert response.status_code == 404
    assert response.json() == {"detail": "Alert not found"}


def test_database_generated_ids_after_delete(client, test_engine):
    assert client.delete("/alerts/2").status_code == 201
    created = client.post("/alerts", json={"title": "new", "level": "warning"})
    assert created.status_code == 201
    assert created.json() == {"id": 5, "title": "new", "level": "warning"}
    with Session(test_engine) as db:
        assert db.get(Alert, 2) is None
        assert db.get(Alert, 5).title == "new"
    listing = client.get("/alerts?page=2&page_size=2").json()
    assert listing == {
        "total": 4, "page": 2, "page_size": 2,
        "items": [
            {"id": 4, "level": "info", "title": "备份完成"},
            created.json(),
        ],
    }


@pytest.mark.parametrize("page,page_size", [(0, 2), (-1, 2), (1, 0), (1, -1)])
def test_pagination_preserves_slice_behavior(client, page, page_size):
    start = (page - 1) * page_size
    expected = [1, 2, 3, 4][start:start + page_size]
    response = client.get("/alerts", params={"page": page, "page_size": page_size})
    assert response.status_code == 200
    assert response.json()["total"] == 4
    assert [item["id"] for item in response.json()["items"]] == expected


@pytest.mark.parametrize("limit,expected", [(0, []), (-1, [1]), (10, [1, 3])])
def test_level_limit_preserves_slice_behavior(client, limit, expected):
    response = client.get("/alerts/warning", params={"limit": limit})
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == expected
