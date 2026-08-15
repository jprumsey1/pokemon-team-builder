"""The Pokedex, to be filtered client-side."""

from collections.abc import Sequence

from fastapi import APIRouter
from sqlalchemy import select

from app.api.dependencies import SessionDep
from app.models import Pokemon
from app.schemas import PokemonOut

router = APIRouter(tags=["pokemon"])


@router.get("", response_model=list[PokemonOut])
async def list_pokemon(db: SessionDep) -> Sequence[Pokemon]:
    # Sorted so variants sit directly under the base form
    # (i.e. Mega Charizard X next to Charizard)
    rows = await db.scalars(
        select(Pokemon).order_by(
            Pokemon.species_id, Pokemon.is_default.desc(), Pokemon.id
        )
    )
    return rows.all()
