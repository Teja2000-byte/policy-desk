import httpx
import pytest

from src.ui_client import APIError, request_api


def test_ui_sends_bearer_token_only_in_header(monkeypatch):
    calls = []

    def request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        return httpx.Response(200, json={"items": []})

    monkeypatch.setattr("httpx.request", request)
    assert request_api("GET", "/tickets", base_url="http://localhost:8000/", token="private-token") == {
        "items": []
    }
    assert calls[0][1] == "http://localhost:8000/tickets"
    assert calls[0][2]["headers"] == {"Authorization": "Bearer private-token"}


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(503, json={"detail": "Unavailable"}),
        httpx.Response(422, json={"detail": [{"loc": ["body", "email"], "msg": "Invalid email"}]}),
        httpx.Response(502, text="upstream error"),
    ],
)
def test_ui_renders_service_errors(monkeypatch, response):
    monkeypatch.setattr("httpx.request", lambda *args, **kwargs: response)
    with pytest.raises(APIError) as exc:
        request_api("POST", "/tickets", base_url="http://localhost:8000")
    assert exc.value.status == response.status_code


def test_ui_network_failure_has_actionable_message(monkeypatch):
    def fail(*args, **kwargs):
        raise httpx.ConnectError("internal")

    monkeypatch.setattr("httpx.request", fail)
    with pytest.raises(APIError, match="Start the backend"):
        request_api("GET", "/health", base_url="http://localhost:8000")
