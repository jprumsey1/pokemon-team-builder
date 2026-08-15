"""User teams, members, and alerts derived from team members."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import delete, exists, select
from sqlalchemy.orm import joinedload, selectinload

from app.api.dependencies import CurrentUser, SessionDep
from app.models import Pokemon, PokemonChangeEvent, Team, TeamPokemon
from app.schemas import AlertOut, CounterOut, TeamIn, TeamMembersIn, TeamOut

router = APIRouter(tags=["teams"])

ALERT_WINDOW = timedelta(days=7)


async def _load_team(db: SessionDep, user_id: int, team_id: int) -> Team:
    """Someone else's team is a 404, not a 403 — a 403 confirms the id exists."""
    team = await db.scalar(
        select(Team)
        .where(Team.id == team_id, Team.user_id == user_id)
        .options(selectinload(Team.members))
    )
    if team is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Team not found")
    return team


@router.get("")
async def list_teams(user: CurrentUser, db: SessionDep) -> list[TeamOut]:
    teams = await db.scalars(
        select(Team)
        .where(Team.user_id == user.id)
        .order_by(Team.created_at)
        .options(selectinload(Team.members))
    )
    return [TeamOut.model_validate(team) for team in teams]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_team(body: TeamIn, user: CurrentUser, db: SessionDep) -> TeamOut:
    team = Team(user_id=user.id, name=body.name)
    db.add(team)
    await db.commit()
    return TeamOut.model_validate(await _load_team(db, user.id, team.id))


@router.patch("/{team_id}")
async def rename_team(
    team_id: int, body: TeamIn, user: CurrentUser, db: SessionDep
) -> TeamOut:
    team = await _load_team(db, user.id, team_id)
    team.name = body.name
    await db.commit()
    return TeamOut.model_validate(team)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(team_id: int, user: CurrentUser, db: SessionDep) -> Response:
    team = await _load_team(db, user.id, team_id)
    await db.delete(team)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{team_id}/members")
async def set_members(
    team_id: int, body: TeamMembersIn, user: CurrentUser, db: SessionDep
) -> TeamOut:
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
    # Re-querying would hand back the identity map's already-loaded collection —
    # the roster we just replaced. Only a refresh re-reads it.
    await db.refresh(team, ["members"])
    return TeamOut.model_validate(team)


@router.post("/{team_id}/counter")
async def counter_team(team_id: int, user: CurrentUser, db: SessionDep) -> CounterOut:
    await _load_team(db, user.id, team_id)
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "Counter team not built yet")


@router.get("/alerts")
async def list_alerts(user: CurrentUser, db: SessionDep) -> list[AlertOut]:
    """Changes in the last 7 days to Pokémon this user has rostered."""
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
    return [AlertOut.model_validate(event) for event in events]
