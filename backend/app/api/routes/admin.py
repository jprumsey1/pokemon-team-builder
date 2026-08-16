"""Admin-only endpoints, meant for triggering background administrative tasks on demand."""

from typing import Annotated

from fastapi import APIRouter, Body

from app.api.dependencies import SessionDep
from app.lib.sync import SyncPokemonResult, sync_pokemon

router = APIRouter(tags=["admin"])


@router.post("/sync")
async def trigger_sync_pokemon(
    db: SessionDep, pokemon_ids: Annotated[list[int] | None, Body()] = None
) -> SyncPokemonResult:
    """Execute the daily Pokemon data synchronization on demand.

    Normally executed as part of the daily sync; this endpoint is mainly for
    demonstration purposes."""
    return await sync_pokemon(db, pokemon_ids)
