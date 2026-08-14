"""Settings, database resources, and the injectable dependencies built on them.

Deliberately free of FastAPI imports for now so `app.core.ingest` can take
`SessionLocal` without pulling the web layer into the pipeline.
"""

from collections.abc import AsyncGenerator

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


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

engine = create_async_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = async_sessionmaker(
    engine,
    # Without this, reading an attribute after commit lazy-loads and raises
    # MissingGreenlet under asyncio.
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
