from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Load .env from the repo root regardless of the current working directory
        env_file=Path(__file__).resolve().parent.parent / ".env",
        # Unknown keys in .env are ignored instead of failing startup
        extra="ignore",
    )

    # Required: startup fails with a clear error if these are missing
    database_url: str
    secret_key: str

    algorithm: str = "HS256"
    access_token_expire_minutes: int = 20

    # Only the test suite needs this
    test_database_url: str | None = None


settings = Settings()
