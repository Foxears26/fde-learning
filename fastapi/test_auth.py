from urllib.parse import parse_qs, urlparse

import httpx
import pytest
from fastapi.testclient import TestClient

from main import app
from routers import auth
import api_client


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("GITHUB_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("GITHUB_CLIENT_SECRET", "test-client-secret")
    with TestClient(app) as client:
        yield client


def mock_github(monkeypatch, handler):
    client_class = auth.APIClient
    monkeypatch.setattr(
        auth, "APIClient",
        lambda *args, **kwargs: client_class(
            *args, transport=httpx.MockTransport(handler), **kwargs
        ),
    )
    monkeypatch.setattr(api_client.time, "sleep", lambda seconds: None)


def test_login_redirect_without_api_key(client):
    response = client.get("/login", follow_redirects=False)
    assert response.status_code == 302
    location = urlparse(response.headers["location"])
    assert (location.scheme, location.netloc, location.path) == (
        "https", "github.com", "/login/oauth/authorize"
    )
    assert parse_qs(location.query) == {
        "client_id": ["test-client-id"],
        "redirect_uri": ["http://localhost:8000/auth/callback"],
        "scope": ["read:user"],
    }


def test_callback_without_api_key(client, monkeypatch):
    requests = []

    def github(request):
        requests.append(request)
        if request.url.path == "/login/oauth/access_token":
            assert request.method == "POST"
            assert str(request.url) == "https://github.com/login/oauth/access_token"
            assert request.headers["accept"] == "application/json"
            assert parse_qs(request.content.decode()) == {
                "client_id": ["test-client-id"],
                "client_secret": ["test-client-secret"],
                "code": ["test-code"],
                "redirect_uri": ["http://localhost:8000/auth/callback"],
            }
            return httpx.Response(200, json={"access_token": "test-token"})
        assert request.method == "GET"
        assert str(request.url) == "https://api.github.com/user"
        assert request.headers["authorization"] == "Bearer test-token"
        return httpx.Response(200, json={"login": "octocat"})

    mock_github(monkeypatch, github)
    response = client.get("/auth/callback", params={"code": "test-code"})
    assert response.status_code == 200
    assert response.json() == {"login": "octocat", "message": "欢迎 octocat"}
    assert len(requests) == 2


def test_callback_requires_code(client):
    assert client.get("/auth/callback").status_code == 422


def test_callback_rejected_code(client, monkeypatch):
    def github(request):
        assert request.url.path == "/login/oauth/access_token"
        return httpx.Response(200, json={"error": "bad_verification_code"})

    mock_github(monkeypatch, github)
    response = client.get("/auth/callback?code=invalid")
    assert response.status_code == 400
    assert response.json() == {"detail": "GitHub authorization failed"}


@pytest.mark.parametrize("failure", ["token_http", "user_http", "timeout", "invalid_json"])
def test_callback_upstream_failure(client, monkeypatch, failure):
    def github(request):
        if failure == "timeout":
            raise httpx.ReadTimeout("timeout", request=request)
        if failure == "invalid_json":
            return httpx.Response(200, text="invalid json")
        if failure == "token_http" or request.url.path == "/user":
            return httpx.Response(503)
        return httpx.Response(200, json={"access_token": "test-token"})

    mock_github(monkeypatch, github)
    response = client.get("/auth/callback?code=test-code")
    assert response.status_code == 502
    assert "test-token" not in response.text
    assert "test-client-secret" not in response.text


def test_existing_routes_without_oauth_configuration(monkeypatch):
    monkeypatch.delenv("GITHUB_CLIENT_ID", raising=False)
    monkeypatch.delenv("GITHUB_CLIENT_SECRET", raising=False)
    with TestClient(app) as client:
        assert client.get("/hello").json() == {"message": "Hello World"}
        assert client.get("/alerts").status_code == 401
