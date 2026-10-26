from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

import httpx
import pytest

import api_client
from api_client import APIClient


@pytest.fixture
def waits(monkeypatch):
    recorded = []
    monkeypatch.setattr(api_client.time, "sleep", recorded.append)
    monkeypatch.setattr(api_client.random, "uniform", lambda low, high: 0.25)
    return recorded


def test_429_twice_then_success(waits):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(429 if len(requests) <= 2 else 200, json={"ok": True})

    with APIClient("https://example.com/api/", transport=httpx.MockTransport(handler)) as client:
        response = client.get("items")
    assert response.json() == {"ok": True}
    assert len(requests) == 3
    assert str(requests[0].url) == "https://example.com/api/items"
    assert requests[0].method == "GET"
    assert requests[0].extensions["timeout"] == {
        "connect": 5.0, "read": 10.0, "write": 10.0, "pool": 10.0,
    }
    assert waits == [1.25, 2.25]


@pytest.mark.parametrize("status", [429, 500, 503, 599])
def test_exhausted_retries_raise(status, waits):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(status)

    with APIClient("https://example.com", transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(httpx.HTTPStatusError) as error:
            client.get("/fail")
    assert error.value.response.status_code == status
    assert len(requests) == 4
    assert waits == [1.25, 2.25, 4.25]


@pytest.mark.parametrize("status", [400, 401, 403, 404, 422])
def test_other_4xx_do_not_retry(status, waits):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(status)

    with APIClient("https://example.com", transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(httpx.HTTPStatusError):
            client.get("/fail")
    assert len(requests) == 1
    assert waits == []


@pytest.mark.parametrize("header, expected", [("3", 3.0), ("0", 0.0), ("bad", 1.25), ("-1", 1.25)])
def test_retry_after_seconds_or_invalid_fallback(header, expected, waits):
    responses = iter([httpx.Response(429, headers={"Retry-After": header}), httpx.Response(200)])
    transport = httpx.MockTransport(lambda request: next(responses))
    with APIClient("https://example.com", transport=transport) as client:
        assert client.get("/").status_code == 200
    assert waits == [expected]


def test_retry_after_http_date(waits):
    future = datetime.now(timezone.utc) + timedelta(seconds=30)
    responses = iter([
        httpx.Response(429, headers={"Retry-After": format_datetime(future, usegmt=True)}),
        httpx.Response(200),
    ])
    with APIClient("https://example.com", transport=httpx.MockTransport(lambda request: next(responses))) as client:
        client.get("/")
    assert len(waits) == 1
    assert 28 <= waits[0] <= 30


@pytest.mark.parametrize("exception", [httpx.ReadTimeout, httpx.ConnectError])
def test_transport_errors_do_not_retry(exception, waits):
    requests = []

    def handler(request):
        requests.append(request)
        raise exception("simulated failure", request=request)

    timeout = httpx.Timeout(1.0, connect=0.5)
    with APIClient("https://example.com", timeout=timeout, transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(exception):
            client.get("/")
    assert len(requests) == 1
    assert requests[0].extensions["timeout"]["read"] == 1.0
    assert requests[0].extensions["timeout"]["connect"] == 0.5
    assert waits == []


def test_zero_retries(waits):
    with APIClient("https://example.com", max_retries=0, transport=httpx.MockTransport(lambda request: httpx.Response(500))) as client:
        with pytest.raises(httpx.HTTPStatusError):
            client.get("/")
    assert waits == []


@pytest.mark.parametrize("value, exception", [(-1, ValueError), (1.5, TypeError), (True, TypeError)])
def test_invalid_max_retries(value, exception):
    with pytest.raises(exception):
        APIClient("https://example.com", max_retries=value)
