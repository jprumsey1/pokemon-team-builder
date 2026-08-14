from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Matches docker-compose.yml
    database_url: str = "postgresql+asyncpg://ptb:ptb@localhost:5432/ptb"

    pokeapi_base_url: str = "https://pokeapi.co/api/v2"

    # Dev defaults
    session_secret: str = "dev-secret"
    admin_secret: str = "dev-admin-secret"

    @field_validator("database_url")
    @classmethod
    def _require_async_driver(cls, v: str) -> str:
        # Hosted providers might postgres:// or postgresql://;
        # ensure asyncpg driver is used; otherwise SQLAlchemy might fail with "Can't load plugin"
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql://", 1)
        if v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


settings = Settings()
