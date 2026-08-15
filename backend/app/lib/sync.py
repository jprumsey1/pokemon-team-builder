"""Sync PokéAPI data to our tables.


Trim payloads to data the team builder app cares about.
Logs what changed as a `PokemonChangeEvent`.

Changes are rare and PokeAPI is a free, public API, so this
should be run as a periodic background task.
"""

import asyncio
import logging
from dataclasses import dataclass

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import engine, session_factory
from app.lib.pokeapi import PokeAPIClient, id_from_url
from app.models import Pokemon, PokemonChangeEvent, TypeMatchup

logger = logging.getLogger(__name__)

# Fields that trigger an alert/PokemonChangeEvent
ALERTING_FIELDS = (
    "name",
    "type_1",
    "type_2",
    "hp",
    "attack",
    "defense",
    "special_attack",
    "special_defense",
    "speed",
)
MUTABLE_FIELDS = tuple(
    column.key for column in Pokemon.__table__.columns if column.key != "id"
)


@dataclass(slots=True)
class SyncPokemonResult:
    checked: int = 0
    inserted: int = 0
    updated: int = 0
    alerted: int = 0  # subset of `updated` that moved an alerting field
    failed: int = 0


async def sync_pokemon(session: AsyncSession) -> SyncPokemonResult:
    """Fetch pokemon data from PokéAPI and synchronize it with the local database."""
    async with PokeAPIClient() as client:
        pokemon_ids = await client.get_all_pokemon_ids()
        logger.info("syncing %d pokemon", len(pokemon_ids))

        result = SyncPokemonResult(checked=len(pokemon_ids))
        cached_by_id = {
            pokemon.id: pokemon for pokemon in await session.scalars(select(Pokemon))
        }

        async for pokemon_id, raw in client.iter_pokemon(pokemon_ids):
            if raw is None:
                result.failed += 1
                continue

            upstream = _trim(raw)
            cached = cached_by_id.get(pokemon_id)
            if cached is None:
                # Inserts never emit events, only changes
                session.add(Pokemon(**upstream))
                result.inserted += 1
                continue

            changed_fields = [
                field
                for field in MUTABLE_FIELDS
                if getattr(cached, field) != upstream[field]
            ]
            if not changed_fields:
                continue
            alerting_changes = []
            for field in changed_fields:
                if field in ALERTING_FIELDS:
                    alerting_changes.append(
                        {
                            "field": field,
                            "from": getattr(cached, field),
                            "to": upstream[field],
                        }
                    )
                setattr(cached, field, upstream[field])

            result.updated += 1
            if alerting_changes:
                session.add(
                    PokemonChangeEvent(pokemon_id=cached.id, changes=alerting_changes)
                )
                result.alerted += 1

    await session.commit()
    logger.info("sync complete: %s", result)
    return result


async def sync_type_matchup(session: AsyncSession) -> int:
    """Replace the 18x18 type matchup chart from upstream. Returns the row count."""
    async with PokeAPIClient() as client:
        damage_relations = await client.get_type_damage_relations()

    type_matchups = {(a, d): 1.0 for a in damage_relations for d in damage_relations}
    for name, relations in damage_relations.items():
        # Ingest attacking side only (`damage_to`) and
        # skip the defending side (`damage_from`) to avoid double-counting.
        for key, multiplier in (
            ("double_damage_to", 2.0),
            ("half_damage_to", 0.5),
            ("no_damage_to", 0.0),
        ):
            for other in relations[key]:
                # Relations can name a type outside the 18, so skip rather than KeyError.
                if (name, other["name"]) in type_matchups:
                    type_matchups[(name, other["name"])] = multiplier

    await session.execute(delete(TypeMatchup))
    session.add_all(
        TypeMatchup(attacking_type=a, defending_type=d, multiplier=m)
        for (a, d), m in type_matchups.items()
    )
    await session.commit()
    logger.info("type chart seeded: %d matchups", len(type_matchups))
    return len(type_matchups)


def _trim(raw_pokemon: dict) -> dict:
    """Convert one PokéAPI /pokemon payload down to our thirteen columns."""
    types = {t["slot"]: t["type"]["name"] for t in raw_pokemon["types"]}
    stats = {s["stat"]["name"]: s["base_stat"] for s in raw_pokemon["stats"]}
    return {
        "id": raw_pokemon["id"],
        "name": raw_pokemon["name"],
        "species_id": id_from_url(raw_pokemon["species"]["url"]),
        "is_default": raw_pokemon["is_default"],
        "type_1": types[1],
        "type_2": types.get(2),
        "hp": stats["hp"],
        "attack": stats["attack"],
        "defense": stats["defense"],
        "special_attack": stats["special-attack"],
        "special_defense": stats["special-defense"],
        "speed": stats["speed"],
        "sprite_url": raw_pokemon["sprites"]["front_default"],
    }


async def sync_all() -> None:
    """Run a full sync of relevant PokeAPI data to the team builder database.

    Only needs to be run once on initial setup to seed Pokemon and 18 base types.
    """
    async with session_factory() as session:
        await sync_type_matchup(session)
        await sync_pokemon(session)
    await engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    # httpx logs one line per request
    logging.getLogger("httpx").setLevel(logging.WARNING)
    asyncio.run(sync_all())
