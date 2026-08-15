"""Admin-only endpoints, meant for triggering background administrative tasks on demand."""

from dataclasses import asdict

from fastapi import APIRouter

from app.api.dependencies import SessionDep
from app.services.sync import sync_pokemon

router = APIRouter(tags=["admin"])


@router.post("/sync")
async def sync(db: SessionDep) -> dict[str, int]:
    """Execute the daily Pokémon data synchronization on demand.
    
    For demonstration purposes.
    """
    return asdict(await sync_pokemon(db))
