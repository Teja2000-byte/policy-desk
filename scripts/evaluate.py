"""Evaluate real Gemini decisions through the authenticated HTTP API."""

import argparse
import csv
import hashlib
import json
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from src.config import ROOT
from src.schemas import TicketInput


def load_cases(path: Path) -> list[dict]:
    if path.suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as file:
            cases = list(csv.DictReader(file))
        for row in cases:
            row["case_id"] = row["ticket_id"]
            row["expected_action"] = row["resolved_action"]
            for name in ("order_value_inr", "days_since_delivery", "days_since_dispatch"):
                row[name] = (
                    None
                    if row[name] == ""
                    else float(row[name])
                    if name == "order_value_inr"
                    else int(row[name])
                )
        return cases
    return json.loads(path.read_text(encoding="utf-8"))


def ticket_payload(case: dict) -> dict:
    # Strict allowlist: expected_action, issue_type, customer_id, and historical
    # resolved_action cannot leak into the request or the model prompt.
    return TicketInput.model_validate(
        {key: value for key, value in case.items() if key in TicketInput.model_fields}
    ).model_dump()


def evaluate(client, cases: list[dict], headers: dict, delay: float = 0) -> dict:
    results = []
    for index, case in enumerate(cases):
        start = time.perf_counter()
        row = {"case_id": str(case["case_id"]), "expected_action": case["expected_action"]}
        try:
            response = client.post("/tickets", json=ticket_payload(case), headers=headers)
            response.raise_for_status()
            decision = response.json()["decision"]
            row.update(
                actual_action=decision["action"],
                correct=decision["action"] == case["expected_action"],
                reason=decision["reason"],
                sources=decision["sources"],
                policy_version=decision["policy_version"],
            )
        except (httpx.HTTPError, ValueError, KeyError):
            row.update(
                actual_action=None,
                correct=False,
                error="Request failed or returned invalid data; inspect service status and rerun.",
            )
        row["latency_ms"] = round((time.perf_counter() - start) * 1000)
        results.append(row)
        print(
            f"{row['case_id']}: {'PASS' if row['correct'] else 'ERROR' if 'error' in row else 'FAIL'} | expected={row['expected_action']} actual={row['actual_action']}",
            flush=True,
        )
        if index + 1 < len(cases) and delay:
            time.sleep(delay)
    correct = sum(row["correct"] for row in results)
    errors = sum("error" in row for row in results)
    total = len(results)
    return {
        "total": total,
        "correct": correct,
        "incorrect": total - correct - errors,
        "errors": errors,
        "accuracy": correct / total if total else None,
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--cases", type=Path, default=ROOT / "sample_test_cases.json")
    parser.add_argument("--output", type=Path, default=ROOT / "reports/evaluation.json")
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--delay", type=float, default=2, help="Seconds between cases, to reduce quota pressure."
    )
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    if args.delay < 0:
        parser.error("--delay cannot be negative")
    cases = load_cases(args.cases)
    if args.limit:
        cases = cases[: args.limit]
    if not cases:
        parser.error("No cases to evaluate")
    with httpx.Client(base_url=args.base_url, timeout=270) as client:
        try:
            status = client.get("/health")
            status.raise_for_status()
            health = status.json()
            if not health["gemini_configured"]:
                raise SystemExit(
                    "Evaluation NOT RUN: configure GEMINI_API_KEY in the backend .env and restart. No accuracy is claimed."
                )
            credentials = {
                "email": f"evaluation-{secrets.token_hex(6)}@example.com",
                "password": secrets.token_urlsafe(24),
            }
            registration = client.post("/register", json=credentials)
            registration.raise_for_status()
            login = client.post("/login", json=credentials)
            login.raise_for_status()
            headers = {"Authorization": "Bearer " + login.json()["access_token"]}
        except httpx.HTTPError:
            raise SystemExit(
                "Evaluation NOT RUN: start the API and verify registration/login are available."
            ) from None
        report = evaluate(client, cases, headers, args.delay)
    report.update(
        provider="gemini",
        model=health["model"],
        embedding_model=health["embedding_model"],
        timestamp=datetime.now(timezone.utc).isoformat(),
        dataset=args.cases.name,
        dataset_sha256=hashlib.sha256(args.cases.read_bytes()).hexdigest(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"\n{report['total']} test cases\nCorrect: {report['correct']}\nIncorrect: {report['incorrect']}\nErrors: {report['errors']}\nAccuracy: {report['accuracy']:.1%}\nReport: {args.output}"
    )
    raise SystemExit(0 if report["correct"] == report["total"] else 1)


if __name__ == "__main__":
    main()
