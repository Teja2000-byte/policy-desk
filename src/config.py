from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore", hide_input_in_errors=True)

    gemini_api_key: SecretStr = SecretStr("")
    jwt_secret: SecretStr
    gemini_model: str = "gemini-2.5-flash"
    embedding_model: str = "gemini-embedding-001"
    embedding_dimensions: int = Field(default=768, ge=128, le=3072)
    database_path: Path = ROOT / "storage/app.db"
    knowledge_base_path: Path = ROOT / "knowledge_base"
    jwt_expiry_minutes: int = Field(default=60, ge=1, le=1440)
    retrieval_documents: int = Field(default=3, ge=1, le=6)
    provider_timeout_seconds: int = Field(default=30, ge=5, le=60)

    @field_validator("jwt_secret")
    @classmethod
    def strong_secret(cls, value: SecretStr) -> SecretStr:
        raw = value.get_secret_value()
        if len(raw) < 32 or raw.lower().startswith(("replace", "your-", "change")):
            raise ValueError(
                "JWT_SECRET must be a random secret of at least 32 characters. Run python scripts/setup.py."
            )
        return value
