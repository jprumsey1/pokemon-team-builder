"""User teams, members, and alerts derived from team members."""

import random
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.api.dependencies import CurrentUser, SessionDep
from app.lib.counter_team import TypeMatchupChart, build_counter_team
from app.models import Pokemon, PokemonChangeEvent, Team, TeamPokemon, TypeMatchup
from app.schemas import (
    AlertOut,
    CounterTeamIn,
    PokemonOut,
    TeamIn,
    TeamMemberOut,
    TeamMembersIn,
    TeamOut,
)

router = APIRouter(tags=["teams"])

ALERT_WINDOW = timedelta(days=7)


@router.get("", response_model=list[TeamOut])
async def list_teams(user: CurrentUser, db: SessionDep) -> Sequence[Team]:
    teams = await db.scalars(
        select(Team)
        .where(Team.user_id == user.id)
        .order_by(Team.created_at)
        .options(selectinload(Team.members))
    )
    return teams.all()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TeamOut)
async def create_team(body: TeamIn, user: CurrentUser, db: SessionDep) -> Team:
    team = Team(user_id=user.id, name=body.name)
    db.add(team)
    await db.commit()
    return await _load_team(db, user.id, team.id)


@router.get("/alerts", response_model=list[AlertOut])
async def list_alerts(
    user: CurrentUser, db: SessionDep
) -> Sequence[PokemonChangeEvent]:
    """Changes within ALERT_WINDOW to Pokémon this user has rostered.

    Declared before the /{team_id} routes so it is not shadowed by them.
    """
    pokemon_rostered_by_user = (
        select(TeamPokemon)
        .join(Team, Team.id == TeamPokemon.team_id)
        .where(
            TeamPokemon.pokemon_id == PokemonChangeEvent.pokemon_id,
            Team.user_id == user.id,
        )
    )
    events = await db.scalars(
        select(PokemonChangeEvent)
        .where(
            PokemonChangeEvent.detected_at > datetime.now(UTC) - ALERT_WINDOW,
            exists(pokemon_rostered_by_user),
        )
        .order_by(PokemonChangeEvent.detected_at.desc())
        .options(joinedload(PokemonChangeEvent.pokemon))
    )
    return events.all()


@router.patch("/{team_id}", response_model=TeamOut)
async def rename_team(
    team_id: int, body: TeamIn, user: CurrentUser, db: SessionDep
) -> Team:
    team = await _load_team(db, user.id, team_id)
    team.name = body.name
    await db.commit()
    return team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(team_id: int, user: CurrentUser, db: SessionDep) -> Response:
    team = await _load_team(db, user.id, team_id)
    await db.delete(team)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{team_id}/members", response_model=TeamOut)
async def set_members(
    team_id: int, body: TeamMembersIn, user: CurrentUser, db: SessionDep
) -> Team:
    """Takes the complete ordered roster, so add, remove and reorder are one call."""
    team = await _load_team(db, user.id, team_id)

    known = set(
        await db.scalars(select(Pokemon.id).where(Pokemon.id.in_(body.pokemon_ids)))
    )
    if unknown := sorted(set(body.pokemon_ids) - known):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, f"Unknown pokemon ids: {unknown}"
        )

    # Core delete() runs immediately; letting the unit of work do it would emit the
    # INSERTs first and collide on (team_id, position). See SQLAlchemy #2501.
    await db.execute(delete(TeamPokemon).where(TeamPokemon.team_id == team.id))
    db.add_all(
        TeamPokemon(team_id=team.id, position=position, pokemon_id=pokemon_id)
        for position, pokemon_id in enumerate(body.pokemon_ids)
    )
    await db.commit()
    # Re-querying would hand back the identity map's already-loaded collection,
    # the roster we just replaced.
    await db.refresh(team, ["members"])
    return team


@router.post("/{team_id}/counter")
async def counter_team(
    team_id: int,
    body: CounterTeamIn,
    user: CurrentUser,
    db: SessionDep,
) -> list[TeamMemberOut]:
    """A counter for each member matched by position.

    Not idempotent, may vary on each call."""
    team = await _load_team(db, user.id, team_id)
    if not team.members:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "Team has no members to counter"
        )
    opposing = [member.pokemon for member in team.members]
    opposing_pokemon_ids = {pokemon.id for pokemon in opposing}
    candidates = await db.scalars(
        select(Pokemon).where(Pokemon.id.notin_(opposing_pokemon_ids))
    )
    type_matchup_chart = await _get_type_matchup_chart(db)
    picks = build_counter_team(
        opposing,
        candidates.all(),
        type_matchup_chart,
        random.Random(),
        stat_metric=body.stat_metric,
    )
    return [
        TeamMemberOut(position=member.position, pokemon=PokemonOut.model_validate(pick))
        for member, pick in zip(team.members, picks, strict=True)
    ]


async def _load_team(db: AsyncSession, user_id: int, team_id: int) -> Team:
    team = await db.scalar(
        select(Team)
        .where(Team.id == team_id, Team.user_id == user_id)
        .options(selectinload(Team.members))
    )
    if team is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Team not found")
    return team


async def _get_type_matchup_chart(db: AsyncSession) -> TypeMatchupChart:
    """The whole 18x18 chart as chart[attacking][defending]. 324 rows; not worth caching."""
    chart: TypeMatchupChart = {}
    for row in await db.scalars(select(TypeMatchup)):
        chart.setdefault(row.attacking_type, {})[row.defending_type] = row.multiplier
    return chart
