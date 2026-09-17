import time

import httpx
import numpy as np
from google import genai
from google.genai import errors, types

from src.config import Settings
from src.schemas import DecisionOutput


class ProviderUnavailable(Exception):
    """A safe error message; never contains provider response bodies or keys."""


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
                transient = exc.code == 429 or (exc.code is not None and exc.code >= 500)
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
