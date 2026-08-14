"""Operator endpoints. `X-Admin-Secret` is enforced at the include site in main.py."""

from dataclasses import asdict

from fastapi import APIRouter

from app.api.dependencies import SessionDep
from app.services.ingest import sync_pokemon

router = APIRouter(tags=["admin"])


@router.post("/scan")
async def scan(db: SessionDep) -> dict[str, int]:
    """Execute weekly Pokémon data synchronization on demand."""
    return asdict(await sync_pokemon(db))
