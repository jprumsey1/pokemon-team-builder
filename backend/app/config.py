from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Matches docker-compose.yml, so local dev needs no .env.
    database_url: str = "postgresql+asyncpg://ptb:ptb@localhost:5432/ptb"

    @field_validator("database_url")
    @classmethod
    def _require_async_driver(cls, v: str) -> str:
        # Hosted providers hand out postgres:// or postgresql://; without the
        # asyncpg driver SQLAlchemy fails with an opaque "Can't load plugin".

        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql://", 1)
        if v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


settings = Settings()
