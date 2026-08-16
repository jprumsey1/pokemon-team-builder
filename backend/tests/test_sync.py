from sqlalchemy import select

from app.lib.sync import sync_pokemon
from app.models import Pokemon, PokemonChangeEvent
from tests.conftest import stub_pokemon_payload


async def test_sync_pokemon_alerts_on_a_stat(session, pokeapi):
    # seed pikachu, then move its attack upstream
    pokeapi[25] = stub_pokemon_payload(25, "pikachu", ["electric"], attack=55)
    await sync_pokemon(session)
    pokeapi[25] = stub_pokemon_payload(25, "pikachu", ["electric"], attack=60)

    result = await sync_pokemon(session)

    # the event names only the stat that moved
    assert (result.updated, result.alerted) == (1, 1)
    event = (await session.scalars(select(PokemonChangeEvent))).one()
    assert event.changes == [{"field": "attack", "from": 55, "to": 60}]


async def test_sync_pokemon_with_pokemon_ids_checks_only_those(session, pokeapi):
    # two seeded pokemon, both moved upstream
    for pokemon_id, name in ((25, "pikachu"), (1, "bulbasaur")):
        pokeapi[pokemon_id] = stub_pokemon_payload(pokemon_id, name, ["electric"], 55)
    await sync_pokemon(session)
    for pokemon_id, name in ((25, "pikachu"), (1, "bulbasaur")):
        pokeapi[pokemon_id] = stub_pokemon_payload(pokemon_id, name, ["electric"], 60)

    result = await sync_pokemon(session, pokemon_ids=[25])

    # the sweep stops at the named id, leaving the other row behind
    assert (result.checked, result.updated) == (1, 1)
    bulbasaur = await session.get(Pokemon, 1)
    await session.refresh(bulbasaur)
    assert bulbasaur.attack == 55


async def test_sync_pokemon_keeps_going_past_a_malformed_payload(session, pokeapi):
    # pikachu's payload is missing its stats; bulbasaur's is intact
    pokeapi[25] = stub_pokemon_payload(25, "pikachu", ["electric"], attack=55)
    del pokeapi[25]["stats"]
    pokeapi[1] = stub_pokemon_payload(1, "bulbasaur", ["grass"], attack=49)

    result = await sync_pokemon(session)

    # the good row is still committed rather than lost with the bad one
    assert (result.failed, result.inserted) == (1, 1)
    assert (await session.scalars(select(Pokemon.name))).all() == ["bulbasaur"]


async def test_sync_pokemon_does_not_alert_on_a_sprite(session, pokeapi):
    # seed pikachu, then move only its sprite upstream
    pokeapi[25] = stub_pokemon_payload(25, "pikachu", ["electric"], attack=55)
    await sync_pokemon(session)
    pokeapi[25] = stub_pokemon_payload(
        25, "pikachu", ["electric"], attack=55, sprite="https://img/moved.png"
    )

    result = await sync_pokemon(session)

    # the row follows upstream, but sprite_url is not an alerting field
    assert (result.updated, result.alerted) == (1, 0)
    assert (await session.scalars(select(PokemonChangeEvent))).all() == []
    pokemon = await session.get(Pokemon, 25)
    await session.refresh(pokemon)
    assert pokemon.sprite_url == "https://img/moved.png"
