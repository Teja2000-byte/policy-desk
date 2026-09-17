from types import SimpleNamespace

import httpx
import numpy as np
import pytest
from google.genai import errors
from pydantic import SecretStr

from src.provider import GeminiProvider, ProviderUnavailable


def make_provider(settings):
    provider = GeminiProvider(settings)
    provider.client = SimpleNamespace(models=SimpleNamespace())
    return provider


def test_official_sdk_client_configuration_can_be_constructed(settings):
    # No provider call is made; this catches incompatible SDK option names.
    configured = settings.model_copy(update={"gemini_api_key": SecretStr("test-only-not-a-real-key")})
    provider = GeminiProvider(configured)
    assert provider.client is not None
    provider.close()


def test_gemini_embedding_is_validated_and_normalized(settings):
    provider = make_provider(settings)
    calls = []

    def embed(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(embeddings=[SimpleNamespace(values=[2.0] * 128)])

    provider.client.models.embed_content = embed
    result = provider.embed(["A policy"], "RETRIEVAL_DOCUMENT")
    assert result.shape == (1, 128)
    assert np.isclose(np.linalg.norm(result[0]), 1)
    assert calls[0]["config"].task_type == "RETRIEVAL_DOCUMENT"
    assert calls[0]["config"].output_dimensionality == 128


@pytest.mark.parametrize("values", [[], [1, 2], [0] * 128, [float("nan")] * 128, [float("inf")] * 128])
def test_malformed_embeddings_fail_closed(settings, values):
    provider = make_provider(settings)
    provider.client.models.embed_content = lambda **kwargs: SimpleNamespace(
        embeddings=[SimpleNamespace(values=values)]
    )
    with pytest.raises(ProviderUnavailable, match="invalid embedding"):
        provider.embed(["Policy"], "RETRIEVAL_DOCUMENT")


def test_gemini_call_passes_json_schema_and_separate_system_prompt(settings):
    provider = make_provider(settings)
    calls = []

    def generate(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(text='{"example":"response"}')

    provider.client.models.generate_content = generate
    assert provider.generate("system policy", "ticket input") == '{"example":"response"}'
    config = calls[0]["config"]
    assert config.response_mime_type == "application/json"
    assert config.system_instruction == "system policy"
    assert "action" in config.response_json_schema["properties"]
    assert calls[0]["contents"] == "ticket input"


def test_transient_failure_retried_once(settings, monkeypatch):
    provider = make_provider(settings)
    monkeypatch.setattr("src.provider.time.sleep", lambda _: None)
    results = [httpx.ConnectError("sensitive provider detail"), "ok"]

    def call():
        value = results.pop(0)
        if isinstance(value, Exception):
            raise value
        return value

    assert provider._call(call) == "ok"
    assert not results


def test_exhausted_network_failure_sanitizes_error(settings, monkeypatch):
    provider = make_provider(settings)
    monkeypatch.setattr("src.provider.time.sleep", lambda _: None)
    calls = []

    def call():
        calls.append(1)
        raise httpx.ReadTimeout("sensitive-provider-response")

    with pytest.raises(ProviderUnavailable) as exc:
        provider._call(call)
    assert len(calls) == 2
    assert "sensitive-provider-response" not in str(exc.value)


@pytest.mark.parametrize("code,expected_calls", [(400, 1), (401, 1), (403, 1), (429, 2), (500, 2)])
def test_provider_retries_only_transient_api_errors(settings, monkeypatch, code, expected_calls):
    provider = make_provider(settings)
    monkeypatch.setattr("src.provider.time.sleep", lambda _: None)
    calls = []

    def call():
        calls.append(1)
        raise errors.ClientError(code, {"error": {"message": "private error", "code": code}})

    with pytest.raises(ProviderUnavailable) as exc:
        provider._call(call)
    assert len(calls) == expected_calls
    assert "private error" not in str(exc.value)
