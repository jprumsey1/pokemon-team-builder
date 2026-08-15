"""The pokedex, to be filtered client-side."""

from fastapi import APIRouter
from sqlalchemy import select

from app.api.dependencies import SessionDep
from app.models import Pokemon
from app.schemas import PokemonOut

router = APIRouter(tags=["pokemon"])


@router.get("")
async def list_pokemon(db: SessionDep) -> list[PokemonOut]:
    # Sorted so variants sit directly under the base form
    # (i.e. Mega Charizard X next to Charizard)
    rows = await db.scalars(
        select(Pokemon).order_by(
            Pokemon.species_id, Pokemon.is_default.desc(), Pokemon.id
        )
    )
    return [PokemonOut.model_validate(row) for row in rows]
