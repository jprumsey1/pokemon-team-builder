"""Shared fixtures. Needs the database container up: `docker compose up -d db`."""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.dependencies import settings
from app.models import Base

SERVER_URL, _ = settings.database_url.rsplit("/", 1)
TEST_DATABASE_URL = f"{SERVER_URL}/ptb_test"


@pytest.fixture(scope="session")
async def engine():
    # CREATE DATABASE can't run inside a transaction, hence AUTOCOMMIT.
    admin = create_async_engine(f"{SERVER_URL}/postgres", isolation_level="AUTOCOMMIT")
    async with admin.connect() as conn:
        if not await conn.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = 'ptb_test'")
        ):
            await conn.execute(text("CREATE DATABASE ptb_test"))
    await admin.dispose()

    # create_all rather than Alembic: alembic/env.py calls asyncio.run(), which
    # raises inside the loop pytest-asyncio is already running. `alembic upgrade
    # head` locally is what exercises the migrations.
    test_engine = create_async_engine(TEST_DATABASE_URL)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    await test_engine.dispose()


@pytest.fixture
async def session(engine):
    # Truncate rather than roll back: the code under test commits, so a rollback
    # fixture would need savepoint mode to undo anything.
    tables = ", ".join(table.name for table in Base.metadata.sorted_tables)
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE {tables} CASCADE"))
    async with async_sessionmaker(engine, expire_on_commit=False)() as open_session:
        yield open_session
