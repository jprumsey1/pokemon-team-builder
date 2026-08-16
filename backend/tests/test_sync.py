from sqlalchemy import select

from app.lib.sync import sync_pokemon
from app.models import Pokemon, PokemonChangeEvent
from tests.conftest import stub_pokemon_payload


async def test_sync_pokemon_alerts_on_a_stat(session, pokeapi):
    # Arrange — seed pikachu, then move its attack upstream
    pokeapi[25] = stub_pokemon_payload(25, "pikachu", ["electric"], attack=55)
    await sync_pokemon(session)
    pokeapi[25] = stub_pokemon_payload(25, "pikachu", ["electric"], attack=60)

    # Act
    result = await sync_pokemon(session)

    # Assert — one update, and an event naming only the stat that moved
    assert (result.updated, result.alerted) == (1, 1)
    event = (await session.scalars(select(PokemonChangeEvent))).one()
    assert event.changes == [{"field": "attack", "from": 55, "to": 60}]


async def test_sync_pokemon_with_pokemon_ids_checks_only_those(session, pokeapi):
    # Arrange — two seeded pokemon, both moved upstream
    for pokemon_id, name in ((25, "pikachu"), (1, "bulbasaur")):
        pokeapi[pokemon_id] = stub_pokemon_payload(pokemon_id, name, ["electric"], 55)
    await sync_pokemon(session)
    for pokemon_id, name in ((25, "pikachu"), (1, "bulbasaur")):
        pokeapi[pokemon_id] = stub_pokemon_payload(pokemon_id, name, ["electric"], 60)

    # Act
    result = await sync_pokemon(session, pokemon_ids=[25])

    # Assert — the sweep stops at the named id, leaving the other row behind
    assert (result.checked, result.updated) == (1, 1)
    bulbasaur = await session.get(Pokemon, 1)
    await session.refresh(bulbasaur)
    assert bulbasaur.attack == 55


async def test_sync_pokemon_does_not_alert_on_a_sprite(session, pokeapi):
    # Arrange — seed pikachu, then move only its sprite upstream
    pokeapi[25] = stub_pokemon_payload(25, "pikachu", ["electric"], attack=55)
    await sync_pokemon(session)
    pokeapi[25] = stub_pokemon_payload(
        25, "pikachu", ["electric"], attack=55, sprite="https://img/moved.png"
    )

    # Act
    result = await sync_pokemon(session)

    # Assert — the row follows upstream, but a CDN reshuffle alerts nobody
    assert (result.updated, result.alerted) == (1, 0)
    assert (await session.scalars(select(PokemonChangeEvent))).all() == []
    pokemon = await session.get(Pokemon, 25)
    await session.refresh(pokemon)
    assert pokemon.sprite_url == "https://img/moved.png"
