"""Admin-only endpoints, meant for triggering background administrative tasks on demand."""

from fastapi import APIRouter

from app.api.dependencies import SessionDep
from app.services import sync as sync_service
from app.services.sync import SyncPokemonResult

router = APIRouter(tags=["admin"])


@router.post("/sync")
async def sync_pokemon(db: SessionDep) -> SyncPokemonResult:
    """Execute the daily Pokémon data synchronization on demand.

    For demonstration purposes.
    """
    return await sync_service.sync_pokemon(db)


@router.post("/sync-type-matchup")
async def sync_type_matchup(db: SessionDep) -> int:
    """Seed the type chart. Needed once per fresh database; the chart never changes."""
    return await sync_service.sync_type_matchup(db)
