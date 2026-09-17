import json
import re
import shutil

import numpy as np
import pytest
from fastapi.testclient import TestClient

from src.api import create_app
from src.config import ROOT, Settings


class TestProvider:
    """Deterministic test double. Never selected by the production application.

    This tests plumbing and validation, NOT Gemini reasoning or embedding quality.
    """

    __test__ = False

    def __init__(self):
        self.embedded = []
        self.generated = []
        self.responses = []
        self.dimensions = 128

    def embed(self, texts, task_type):
        self.embedded.append((texts, task_type))
        vectors = []
        for text in texts:
            words = text.lower().splitlines()[0]
            features = [
                1 + 8 * bool(re.search(term, words))
                for term in (
                    "damag|crushed|broken",
                    "return|unopened",
                    "shipping|dispatch|parcel",
                    "wrong|flavour|chocolate",
                    "defect|functional",
                    "cancel",
                )
            ]
            vector = np.array(features + [0] * (self.dimensions - len(features)), dtype=np.float32)
            vectors.append(vector / np.linalg.norm(vector))
        return np.stack(vectors)

    def generate(self, system, prompt):
        self.generated.append((system, prompt))
        if self.responses:
            value = self.responses.pop(0)
            if isinstance(value, Exception):
                raise value
            return value
        context = json.loads(prompt.split("\nYour last response")[0])["policy_context"]
        chunk = next(c for c in context if c["source"] == "damaged_goods.md" and "above ₹2,000" in c["text"])
        quote = next(line for line in chunk["text"].splitlines() if "above ₹2,000" in line)
        return json.dumps(
            {
                "action": "REQUEST_PHOTOS",
                "confidence": 0.91,
                "reason": "The order arrived damaged yesterday and is valued above ₹2,000, so photographs are needed.",
                "sources": ["damaged_goods.md"],
                "evidence": [{"chunk_id": chunk["chunk_id"], "quote": quote}],
                "missing_information": [],
            }
        )

    def close(self):
        pass


@pytest.fixture
def settings(tmp_path):
    kb = tmp_path / "knowledge_base"
    shutil.copytree(ROOT / "knowledge_base", kb)
    return Settings(
        _env_file=None,
        jwt_secret="test-secret-" * 8,
        gemini_api_key="",
        database_path=tmp_path / "test.db",
        knowledge_base_path=kb,
        embedding_dimensions=128,
    )


@pytest.fixture
def provider():
    return TestProvider()


@pytest.fixture
def app(settings, provider):
    return create_app(settings, provider)


@pytest.fixture
def client(app):
    with TestClient(app) as result:
        yield result


def account(client, email="alice@example.com"):
    payload = {"email": email, "password": "test-password-123"}
    assert client.post("/register", json=payload).status_code == 201
    token = client.post("/login", json=payload).json()["access_token"]
    return {"Authorization": "Bearer " + token}


@pytest.fixture
def headers(client):
    return account(client)


@pytest.fixture
def ticket():
    return {
        "message": "My ₹3,500 order arrived damaged yesterday.",
        "order_value_inr": 3500,
        "days_since_delivery": 1,
        "product_type": "non_food",
        "opened_status": "opened",
        "order_status": "delivered",
    }
