import httpx
import pytest
import respx
from sqlalchemy import select

from app.core.config import settings
from app.models import PokemonChangeEvent
from app.services.ingest import sync_pokemon


def stub_pokemon_payload(pokemon_id, name, types, attack):
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
        "sprites": {"front_default": f"https://img/test_{pokemon_id}.png"},
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


async def test_sync_pokemon_records_a_stat_change(session, pokeapi):
    pokeapi[25] = stub_pokemon_payload(25, "pikachu", ["electric"], attack=55)
    await sync_pokemon(session)

    pokeapi[25] = stub_pokemon_payload(25, "pikachu", ["electric"], attack=60)
    result = await sync_pokemon(session)

    # Ensure attack change from 55 to 60 is recorded in pokemon_change_event
    assert (result.updated, result.alerted) == (1, 1)
    event = (await session.scalars(select(PokemonChangeEvent))).one()
    assert event.changes == [{"field": "attack", "from": 55, "to": 60}]
