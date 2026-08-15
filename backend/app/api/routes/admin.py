"""Admin-only endpoints, meant for triggering background administrative tasks on demand."""

from fastapi import APIRouter

from app.api.dependencies import SessionDep
from app.lib.sync import SyncPokemonResult, sync_pokemon, sync_type_matchup

router = APIRouter(tags=["admin"])


@router.post("/sync")
async def trigger_sync_pokemon(db: SessionDep) -> SyncPokemonResult:
    """Execute the daily Pokémon data synchronization on demand.

    Normally executed as part of the daily sync; this endpoint is mainly for
    demonstration purposes."""
    return await sync_pokemon(db)


@router.post("/sync-type-matchup")
async def trigger_sync_type_matchup(db: SessionDep) -> int:
    """Seed the type chart.

    Needed once per fresh database."""
    return await sync_type_matchup(db)
