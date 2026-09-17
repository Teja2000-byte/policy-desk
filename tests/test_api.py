import json
import sqlite3
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

from src.api import create_app
from src.auth import PASSWORDS
from src.provider import ProviderUnavailable
from src.schemas import Action, DecisionOutput, TicketInput
from tests.conftest import account


def test_register_hash_login_and_me(client, app):
    payload = {"email": "  Alice@EXAMPLE.com ", "password": "a long password "}
    response = client.post("/register", json=payload)
    assert response.status_code == 201
    assert response.json()["email"] == "alice@example.com"
    assert "password" not in response.text
    row = app.state.db.user_by_email("alice@example.com")
    assert row["password_hash"].startswith("$argon2id$")
    assert PASSWORDS.verify(payload["password"], row["password_hash"])
    token = client.post("/login", json=payload).json()
    assert token["token_type"] == "bearer" and token["expires_in"] == 3600
    assert (
        client.get("/me", headers={"Authorization": "Bearer " + token["access_token"]}).json()["id"]
        == response.json()["id"]
    )
    assert client.post("/register", json=payload).status_code == 409
    assert client.post("/login", json={**payload, "password": "a long password"}).status_code == 401


@pytest.mark.parametrize(
    "method,path", [("GET", "/me"), ("GET", "/tickets"), ("GET", "/tickets/1"), ("POST", "/tickets")]
)
def test_protected_endpoints_require_token(client, method, path, ticket):
    response = client.request(method, path, json=ticket if method == "POST" else None)
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "mode",
    [
        "expired",
        "wrong-signature",
        "wrong-audience",
        "missing-exp",
        "none-algorithm",
        "unknown-user",
        "invalid-subject",
    ],
)
def test_reject_bad_tokens(client, settings, headers, mode):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "1",
        "iat": now,
        "exp": now + timedelta(hours=1),
        "iss": "policy-desk",
        "aud": "policy-desk",
    }
    secret = settings.jwt_secret.get_secret_value()
    algorithm = "HS256"
    if mode == "expired":
        payload["exp"] = now - timedelta(seconds=1)
    elif mode == "wrong-signature":
        secret = "different-secret" * 4
    elif mode == "wrong-audience":
        payload["aud"] = "other-app"
    elif mode == "missing-exp":
        del payload["exp"]
    elif mode == "none-algorithm":
        secret, algorithm = "", "none"
    elif mode == "unknown-user":
        payload["sub"] = "9999"
    else:
        payload["sub"] = "not-an-id"
    token = jwt.encode(payload, secret, algorithm=algorithm)
    assert client.get("/me", headers={"Authorization": "Bearer " + token}).status_code == 401


def test_wrong_credentials_generic(client, headers):
    known = client.post("/login", json={"email": "alice@example.com", "password": "wrong-password"})
    unknown = client.post("/login", json={"email": "unknown@example.com", "password": "wrong-password"})
    assert known.status_code == unknown.status_code == 401
    assert known.json() == unknown.json()


def test_alice_cannot_read_bobs_ticket(client, headers, ticket):
    bob = account(client, "bob@example.com")
    bob_ticket = client.post("/tickets", headers=bob, json=ticket)
    assert bob_ticket.status_code == 201, bob_ticket.text
    ticket_id = bob_ticket.json()["id"]
    assert client.get(f"/tickets/{ticket_id}", headers=bob).status_code == 200
    denied = client.get(f"/tickets/{ticket_id}", headers=headers)
    absent = client.get("/tickets/999999", headers=headers)
    assert denied.status_code == absent.status_code == 404
    assert denied.json() == absent.json()
    assert client.get("/tickets", headers=headers).json()["items"] == []
    assert client.get("/tickets", headers=bob).json()["total"] == 1


def test_decision_persists_across_app_restart(client, headers, ticket, settings, provider):
    result = client.post("/tickets", headers=headers, json=ticket)
    assert result.status_code == 201, result.text
    with TestClient(create_app(settings, provider)) as restarted:
        saved = restarted.get(f"/tickets/{result.json()['id']}", headers=headers).json()
        assert saved == result.json()
        assert saved["decision"]["sources"] == ["damaged_goods.md"]
        assert saved["decision"]["retrieved_context"]


def test_invalid_model_response_does_not_create_partial_ticket(client, app, headers, ticket, provider):
    provider.responses = ['{"action":"MAGIC"}', "not json"]
    response = client.post("/tickets", headers=headers, json=ticket)
    assert response.status_code == 502
    assert client.get("/tickets", headers=headers).json()["total"] == 0
    with app.state.db.connect() as conn:
        assert conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0] == 0


def test_provider_failure_is_503_not_a_fake_business_decision(client, headers, ticket, provider):
    provider.responses = [ProviderUnavailable("Gemini is unavailable.")]
    response = client.post("/tickets", headers=headers, json=ticket)
    assert response.status_code == 503
    assert client.get("/tickets", headers=headers).json()["total"] == 0


def test_missing_information_is_saved(client, headers, ticket, provider):
    provider.responses = [
        json.dumps(
            {
                "action": "NEEDS_MORE_INFORMATION",
                "confidence": 0.9,
                "reason": "The product type and delivery date are needed to establish return eligibility.",
                "sources": [],
                "evidence": [],
                "missing_information": [
                    "What type of product is it?",
                    "When was it delivered?",
                    "Is it unopened?",
                ],
            }
        )
    ]
    response = client.post("/tickets", headers=headers, json={**ticket, "message": "I want to return this."})
    assert response.status_code == 201
    assert response.json()["decision"]["missing_information"]


@pytest.mark.parametrize(
    "changes",
    [
        {"days_since_delivery": -1},
        {"days_since_delivery": 1.5},
        {"days_since_delivery": True},
        {"message": "    "},
        {"order_value_inr": -1},
        {"user_id": 2},
        {"resolved_action": "APPROVE_RETURN"},
        {"issue_type": "return"},
        {"order_status": "nonsense"},
        {"message": "x" * 5001},
    ],
)
def test_reject_invalid_ticket_fields(client, headers, ticket, changes):
    assert client.post("/tickets", headers=headers, json={**ticket, **changes}).status_code == 422


def test_history_is_paginated_newest_first(client, headers, ticket):
    ids = [client.post("/tickets", json=ticket, headers=headers).json()["id"] for _ in range(3)]
    page = client.get("/tickets?limit=1&offset=1", headers=headers).json()
    assert page["total"] == 3 and page["items"][0]["id"] == ids[1]
    assert client.get("/tickets?limit=101", headers=headers).status_code == 422
    assert client.get("/tickets?offset=-1", headers=headers).status_code == 422


def test_missing_api_key_fails_cleanly(settings, ticket):
    with TestClient(create_app(settings)) as client:
        headers = account(client)
        assert client.get("/health").json()["gemini_configured"] is False
        result = client.post("/tickets", json=ticket, headers=headers)
        assert result.status_code == 503
        assert "GEMINI_API_KEY" in result.json()["detail"]


@pytest.mark.parametrize("email", [None, 42, [], {}, "invalid-email"])
def test_invalid_email_is_422_not_server_error(client, email):
    assert client.post("/register", json={"email": email, "password": "test-password"}).status_code == 422


def test_database_rolls_back_ticket_if_decision_insert_fails(app, headers, ticket):
    # Deliberately bypass Pydantic to exercise the independent SQL constraint.
    decision = DecisionOutput.model_construct(
        action=Action.REQUEST_PHOTOS,
        reason="Invalid test confidence",
        confidence=2,
        sources=[],
        evidence=[],
        missing_information=[],
    )
    with pytest.raises(sqlite3.IntegrityError):
        app.state.db.save_ticket(1, TicketInput(**ticket), decision, [], "test-model", "test-version", 0)
    assert app.state.db.list_tickets(1, 20, 0)["total"] == 0
