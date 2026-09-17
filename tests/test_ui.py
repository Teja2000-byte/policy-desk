from streamlit.testing.v1 import AppTest

from src.config import ROOT
from src.ui_client import APIError


def test_registration_form_sends_http_requests_then_opens_workspace(monkeypatch):
    calls = []

    def fake_request(method, path, **kwargs):
        calls.append((method, path, kwargs))
        if path == "/health":
            return {"gemini_configured": True}
        if path == "/register":
            return {"id": 1, "email": "test@example.com"}
        if path == "/login":
            return {"access_token": "test-token"}
        if path == "/me":
            return {"id": 1, "email": "test@example.com"}
        raise AssertionError(path)

    monkeypatch.setattr("src.ui_client.request_api", fake_request)
    app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=15).run()
    assert not app.exception
    app.text_input(key="email-True").input("test@example.com")
    app.text_input(key="password-True").input("test-password")
    next(button for button in app.button if button.label == "Create account").click().run()
    assert not app.exception
    assert app.session_state["token"] == "test-token"
    assert [path for _, path, _ in calls if path != "/health"] == ["/register", "/login", "/me"]
    assert any(title.value == "What does the customer need?" for title in app.title)


def test_blank_optional_numbers_and_example_submission(monkeypatch):
    submitted = []

    def fake_request(method, path, **kwargs):
        if path == "/health":
            return {"gemini_configured": True}
        if path == "/tickets":
            submitted.append(kwargs["payload"])
            raise APIError("Test service unavailable", 503)
        raise AssertionError(path)

    monkeypatch.setattr("src.ui_client.request_api", fake_request)
    app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=15)
    app.session_state["token"] = "test-token"
    app.session_state["email"] = "test@example.com"
    app.run()
    assert not app.exception
    assert app.number_input(key="days_since_delivery").value is None
    app.selectbox[0].select("Damaged delivery · ₹3,500").run()
    assert app.number_input(key="days_since_delivery").value == 1
    next(button for button in app.button if button.label.startswith("Generate decision")).click().run()
    assert not app.exception
    assert submitted[0]["order_value_inr"] == 3500
    assert submitted[0]["days_since_dispatch"] is None
    assert any("Test service unavailable" in item.value for item in app.error)


def test_expired_session_clears_private_state(monkeypatch):
    def fake_request(method, path, **kwargs):
        if path == "/health":
            return {"gemini_configured": True}
        raise APIError("Expired", 401)

    monkeypatch.setattr("src.ui_client.request_api", fake_request)
    app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=15)
    app.session_state["token"] = "expired-token"
    app.session_state["email"] = "test@example.com"
    app.run()
    app.radio[0].set_value("History").run()
    assert not app.exception
    assert "token" not in app.session_state
    assert any("expired" in item.value for item in app.info)


def test_result_and_history_render_saved_api_response(monkeypatch, client, headers):
    calls = []

    def through_api(method, path, **kwargs):
        calls.append((method, path))
        response = client.request(
            method,
            path,
            headers={"Authorization": "Bearer " + kwargs["token"]} if kwargs.get("token") else {},
            json=kwargs.get("payload"),
            params=kwargs.get("params"),
        )
        if response.is_error:
            raise APIError(response.json()["detail"], response.status_code)
        return response.json()

    monkeypatch.setattr("src.ui_client.request_api", through_api)
    app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=15)
    app.session_state["token"] = headers["Authorization"].removeprefix("Bearer ")
    app.session_state["email"] = "alice@example.com"
    app.run()
    app.selectbox[0].select("Damaged delivery · ₹3,500").run()
    next(button for button in app.button if button.label.startswith("Generate decision")).click().run()
    assert not app.exception
    assert any("Request photos" in value.value for value in app.success)
    assert any(value.label == "Model confidence" and value.value == "91%" for value in app.metric)
    assert any("damaged_goods.md" in value.label for value in app.expander)
    app.radio[0].set_value("History").run()
    assert not app.exception
    assert ("GET", "/tickets") in calls and ("GET", "/tickets/1") in calls
    assert any("Request photos" in value.value for value in app.success)
    next(button for button in app.button if button.label == "Sign out").click().run()
    assert not app.exception and "token" not in app.session_state
