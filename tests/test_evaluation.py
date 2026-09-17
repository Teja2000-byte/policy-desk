import httpx

from scripts.evaluate import evaluate, load_cases, ticket_payload
from src.config import ROOT


def test_historical_labels_and_customer_identifiers_never_enter_request():
    cases = load_cases(ROOT / "data/tickets.csv")
    assert len(cases) == 214
    for case in cases:
        payload = ticket_payload(case)
        assert (
            not {
                "resolved_action",
                "expected_action",
                "issue_type",
                "customer_id",
                "customer_name",
                "ticket_id",
            }
            & payload.keys()
        )


def test_supplied_five_cases_load_without_modification():
    cases = load_cases(ROOT / "sample_test_cases.json")
    assert len(cases) == 5
    assert cases[0]["expected_action"] == "REQUEST_PHOTOS"
    assert ticket_payload(cases[-1])["days_since_delivery"] is None


def test_extended_cases_are_usable_without_transmitting_expected_policy():
    cases = load_cases(ROOT / "data/extended_test_cases.json")
    assert len(cases) == 40 and len({case["case_id"] for case in cases}) == 40
    for case in cases:
        payload = ticket_payload(case)
        assert not {"scenario", "policy_basis", "expected_action"} & payload.keys()


def test_metrics_count_errors_in_accuracy_denominator():
    responses = [
        httpx.Response(
            201,
            json={
                "decision": {
                    "action": "REQUEST_PHOTOS",
                    "reason": "Test",
                    "sources": [],
                    "policy_version": "test",
                }
            },
        ),
        httpx.Response(
            201,
            json={"decision": {"action": "WRONG", "reason": "Test", "sources": [], "policy_version": "test"}},
        ),
        httpx.Response(503, json={"detail": "Test outage"}),
    ]
    sent = []

    def handle(request):
        sent.append(request.content.decode())
        return responses.pop(0)

    cases = [
        {"case_id": str(i), "message": "Damaged order", "expected_action": "REQUEST_PHOTOS"} for i in range(3)
    ]
    with httpx.Client(transport=httpx.MockTransport(handle), base_url="http://test") as client:
        report = evaluate(client, cases, {})
    assert report["total"] == 3
    assert report["correct"] == report["incorrect"] == report["errors"] == 1
    assert report["accuracy"] == 1 / 3
    assert all("expected_action" not in body for body in sent)
