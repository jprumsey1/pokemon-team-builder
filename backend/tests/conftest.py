"""Shared fixtures. Needs the database container up: `docker compose up -d db`."""

import httpx
import pytest
import respx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.dependencies import get_db
from app.config import settings
from app.main import app
from app.models import Base, Pokemon

SERVER_URL, _ = settings.database_url.rsplit("/", 1)
TEST_DATABASE_URL = f"{SERVER_URL}/ptb_test"

ADMIN_HEADERS = {"X-Admin-Secret": settings.admin_secret}


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


@pytest.fixture
async def client(session):
    """Calls the app in this test's event loop, on this test's session.

    ASGITransport rather than TestClient: TestClient drives the app on a portal
    thread with its own loop, and the session's asyncpg connections belong to
    this one — mixing them raises "attached to a different loop".
    """
    app.dependency_overrides[get_db] = lambda: session
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


def make_pokemon(pokemon_id, name, type_1, type_2=None, **stats):
    """A Pokedex row. Stats default to something plausible; override what a test cares about."""
    return Pokemon(
        id=pokemon_id,
        name=name,
        species_id=pokemon_id,
        is_default=True,
        type_1=type_1,
        type_2=type_2,
        sprite_url=f"https://img/{pokemon_id}.png",
        **{
            "hp": 45,
            "attack": 49,
            "defense": 49,
            "special_attack": 65,
            "special_defense": 65,
            "speed": 45,
            **stats,
        },
    )


def stub_pokemon_payload(pokemon_id, name, types, attack, sprite=None):
    stats = {
        "hp": 35,
        "attack": attack,
        "defense": 40,
        "special-attack": 50,
        "special-defense": 50,
        "speed": 90,
    }
    return {
        "id": pokemon_id,
        "name": name,
        "is_default": True,
        "species": {
            "url": f"{settings.pokeapi_base_url}/pokemon-species/{pokemon_id}/"
        },
        "types": [{"slot": i, "type": {"name": t}} for i, t in enumerate(types, 1)],
        "stats": [{"stat": {"name": k}, "base_stat": v} for k, v in stats.items()],
        "sprites": {"front_default": sprite or f"https://img/test_{pokemon_id}.png"},
    }


@pytest.fixture
def pokeapi():
    """Stubs PokéAPI calls.

    Yields a mutable {id: payload} that can be re-assigned to simulate upstream changes."""
    payloads = {}

    def mock_get_all_pokemon(request):
        urls = [{"url": f"{settings.pokeapi_base_url}/pokemon/{i}/"} for i in payloads]
        return httpx.Response(200, json={"results": urls})

    def mock_get_pokemon(request):
        return httpx.Response(200, json=payloads[int(request.url.path.split("/")[-2])])

    with respx.mock(base_url=settings.pokeapi_base_url) as router:
        router.get(path__regex=r"^/pokemon/\d+/$").mock(side_effect=mock_get_pokemon)
        router.get(path="/pokemon").mock(side_effect=mock_get_all_pokemon)
        yield payloads
