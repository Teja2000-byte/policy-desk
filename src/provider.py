import logging
import time

import httpx
import numpy as np
from google import genai
from google.genai import errors, types

from src.config import Settings
from src.schemas import DecisionOutput

logger = logging.getLogger(__name__)


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


def api_error_message(exc: errors.APIError) -> str:
    """Return fixed guidance, never provider response text or sensitive metadata."""
    if exc.code == 429:
        return quota_message(exc)
    payload = exc.details if isinstance(exc.details, dict) else {}
    payload = payload.get("error", payload)
    payload = payload if isinstance(payload, dict) else {}
    details = payload.get("details", [])
    reasons = {
        item.get("reason")
        for item in details if isinstance(item, dict) and isinstance(item.get("reason"), str)
    } if isinstance(details, list) else set()
    if reasons & {"API_KEY_INVALID", "API_KEY_EXPIRED", "API_KEY_NOT_FOUND", "CREDENTIALS_MISSING"}:
        return "Google rejected the API key. Ask the key owner to check its validity in Google AI Studio."
    if exc.code == 401:
        return "Google could not authenticate this API key. Ask the key owner to check its validity."
    if exc.code == 403:
        return (
            "Google denied access. Ask the key owner to check API restrictions, blocked-key status, "
            "and project/model permissions in Google AI Studio."
        )
    if exc.code == 404:
        return "Google could not find the requested model or API resource. Check model availability and name."
    if exc.code == 400 and payload.get("status") == "FAILED_PRECONDITION":
        return "Google rejected the project's setup. The key owner should check its API eligibility and setup."
    if exc.code == 400:
        return "Google rejected the request. Check API-key validity and the model's supported request settings."
    if exc.code == 504:
        return "Google's Gemini service timed out. Wait before trying again."
    if isinstance(exc.code, int) and exc.code >= 500:
        return "Google's Gemini service is temporarily unavailable or failed internally. Wait before trying again."
    return "Google rejected the Gemini request. Check the backend model configuration and project access."


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

    def _call(self, fn, *, operation="request"):
        if self.client is None:
            raise ProviderUnavailable(
                "Gemini is not configured. Add your own GEMINI_API_KEY to the backend .env and restart."
            )
        for attempt in range(2):
            try:
                return fn()
            except errors.APIError as exc:
                # A one-second retry cannot resolve quota exhaustion; only retry server failures.
                transient = isinstance(exc.code, int) and exc.code >= 500
                if transient and attempt == 0:
                    time.sleep(1)
                    continue
                code = exc.code if isinstance(exc.code, int) else "unknown"
                logger.warning("Gemini %s failed: HTTP %s", operation, code)
                raise ProviderUnavailable(
                    f"{api_error_message(exc)} Failed step: {operation}. Google HTTP status: {code}."
                ) from None
            except (httpx.HTTPError, TimeoutError, OSError):
                if attempt == 0:
                    time.sleep(1)
                    continue
                raise ProviderUnavailable(
                    f"Gemini request timed out or could not connect. Failed step: {operation}. Please retry."
                ) from None

    def embed(self, texts: list[str], task_type: str) -> np.ndarray:
        response = self._call(
            lambda: self.client.models.embed_content(
                model=self.settings.embedding_model,
                contents=texts,
                config=types.EmbedContentConfig(
                    task_type=task_type, output_dimensionality=self.settings.embedding_dimensions
                ),
            ),
            operation="policy retrieval embedding",
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
            ),
            operation="decision generation",
        )
        return response.text or ""

    def close(self):
        if self.client:
            self.client.close()
