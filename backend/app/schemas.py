"""Request and response bodies."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PokemonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    species_id: int
    is_default: bool
    type_1: str
    type_2: str | None
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int
    sprite_url: str | None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class SessionIn(BaseModel):
    username: str = Field(min_length=1, max_length=50)


class TeamMemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    position: int
    pokemon: PokemonOut


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    members: list[TeamMemberOut]


class TeamIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class TeamMembersIn(BaseModel):
    pokemon_ids: list[int] = Field(max_length=6)


class AlertPokemon(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sprite_url: str | None


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pokemon: AlertPokemon
    detected_at: datetime
    # `from` is a keyword, so {field, from, to} can't be a model. Pass the JSONB through.
    changes: list[dict]


class CounterPick(BaseModel):
    pokemon: PokemonOut
    rationale: str


class CounterOut(BaseModel):
    picks: list[CounterPick]
