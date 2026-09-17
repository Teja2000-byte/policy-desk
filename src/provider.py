import time

import httpx
import numpy as np
from google import genai
from google.genai import errors, types

from src.config import Settings
from src.schemas import DecisionOutput


class ProviderUnavailable(Exception):
    """A safe error message; never contains provider response bodies or keys."""


def quota_message(exc: errors.APIError) -> str:
    """Classify structured quota metadata without exposing provider error text."""
    payload = exc.details if isinstance(exc.details, dict) else {}
    payload = payload.get("error", payload)
    details = payload.get("details", []) if isinstance(payload, dict) else []
    for detail in details if isinstance(details, list) else []:
        if not isinstance(detail, dict):
            continue
        violations = detail.get("violations", [])
        for violation in violations if isinstance(violations, list) else []:
            if isinstance(violation, dict) and "perday" in str(
                violation.get("quotaId", "")
            ).lower():
                return (
                    "Gemini's daily request quota has been reached. New decisions can resume "
                    "after the quota resets at midnight Pacific Time. "
                    "Saved decisions remain available in History."
                )
    return (
        "Gemini's request or token limit has been reached. Wait before retrying and check "
        "your project's usage in Google AI Studio. Saved decisions remain available in History."
    )


class GeminiProvider:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = None
        if settings.gemini_api_key.get_secret_value():
            self.client = genai.Client(
                api_key=settings.gemini_api_key.get_secret_value(),
                http_options=types.HttpOptions(
                    timeout=settings.provider_timeout_seconds * 1000,
                    retry_options=types.HttpRetryOptions(attempts=1),
                ),
            )

    def _call(self, fn):
        if self.client is None:
            raise ProviderUnavailable(
                "Gemini is not configured. Add your own GEMINI_API_KEY to the backend .env and restart."
            )
        for attempt in range(2):
            try:
                return fn()
            except errors.APIError as exc:
                if exc.code == 429:
                    # A one-second retry cannot resolve a daily quota and can worsen throttling.
                    raise ProviderUnavailable(quota_message(exc)) from None
                transient = exc.code is not None and exc.code >= 500
                if transient and attempt == 0:
                    time.sleep(1)
                    continue
                raise ProviderUnavailable(
                    "Gemini is unavailable. Check the backend API key, model access, quota, and network; then retry."
                ) from None
            except (httpx.HTTPError, TimeoutError, OSError):
                if attempt == 0:
                    time.sleep(1)
                    continue
                raise ProviderUnavailable(
                    "Gemini request timed out or could not connect. Please retry."
                ) from None

    def embed(self, texts: list[str], task_type: str) -> np.ndarray:
        response = self._call(
            lambda: self.client.models.embed_content(
                model=self.settings.embedding_model,
                contents=texts,
                config=types.EmbedContentConfig(
                    task_type=task_type, output_dimensionality=self.settings.embedding_dimensions
                ),
            )
        )
        try:
            values = np.asarray([item.values for item in response.embeddings], dtype=np.float32)
            if (
                values.shape != (len(texts), self.settings.embedding_dimensions)
                or not np.isfinite(values).all()
            ):
                raise ValueError
            norms = np.linalg.norm(values, axis=1, keepdims=True)
            if (norms <= 0).any():
                raise ValueError
            return values / norms
        except (TypeError, ValueError, AttributeError):
            raise ProviderUnavailable("Gemini returned an invalid embedding response.") from None

    def generate(self, system: str, prompt: str) -> str:
        response = self._call(
            lambda: self.client.models.generate_content(
                model=self.settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    temperature=0,
                    max_output_tokens=4096,
                    response_mime_type="application/json",
                    response_json_schema=DecisionOutput.model_json_schema(),
                ),
            )
        )
        return response.text or ""

    def close(self):
        if self.client:
            self.client.close()
