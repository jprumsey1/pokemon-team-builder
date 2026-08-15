from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select

from app.models import PokemonChangeEvent, TeamPokemon
from tests.conftest import ADMIN_HEADERS, make_pokemon, stub_pokemon_payload


async def sign_in(client, username):
    await client.post("/api/session", json={"username": username})


async def new_team(client, name="Kanto"):
    response = await client.post("/api/teams", json={"name": name})
    return response.json()["id"]


async def test_put_members_replaces_the_whole_roster(client, session):
    # Arrange — a team already holding [1, 2, 3]
    session.add_all(
        [
            make_pokemon(1, "bulbasaur", "grass"),
            make_pokemon(2, "charmander", "fire"),
            make_pokemon(3, "squirtle", "water"),
        ]
    )
    await session.commit()
    await sign_in(client, "ash")
    team_id = await new_team(client)
    await client.put(f"/api/teams/{team_id}/members", json={"pokemon_ids": [1, 2, 3]})

    # Act — reorder, drop one, and carry the same Pokémon twice
    response = await client.put(
        f"/api/teams/{team_id}/members", json={"pokemon_ids": [3, 1, 1]}
    )

    # Assert — the response reflects the write, not the roster it replaced
    assert response.status_code == 200
    members = response.json()["members"]
    assert [member["pokemon"]["id"] for member in members] == [3, 1, 1]
    assert [member["position"] for member in members] == [0, 1, 2]


@pytest.mark.parametrize(
    "pokemon_ids",
    [
        pytest.param([1, 1, 1, 1, 1, 1, 1], id="seven-is-over-the-cap"),
        pytest.param([999], id="no-such-pokemon"),
    ],
)
async def test_put_members_rejects_an_invalid_roster(client, session, pokemon_ids):
    # Arrange
    session.add(make_pokemon(1, "bulbasaur", "grass"))
    await session.commit()
    await sign_in(client, "ash")
    team_id = await new_team(client)

    # Act
    response = await client.put(
        f"/api/teams/{team_id}/members", json={"pokemon_ids": pokemon_ids}
    )

    # Assert
    assert response.status_code == 422


async def test_alerts_returns_one_row_per_event_for_my_roster(client, session):
    # Arrange — three events: mine, someone else's, and mine but expired.
    # Pikachu sits in two of my teams, which a join would report twice.
    session.add_all(
        [
            make_pokemon(25, "pikachu", "electric"),
            make_pokemon(1, "bulbasaur", "grass"),
            make_pokemon(4, "charmander", "fire"),
        ]
    )
    session.add_all(
        [
            PokemonChangeEvent(pokemon_id=25, changes=[{"field": "attack"}]),
            PokemonChangeEvent(pokemon_id=1, changes=[{"field": "attack"}]),
            PokemonChangeEvent(
                pokemon_id=4,
                detected_at=datetime.now(UTC) - timedelta(days=8),
                changes=[{"field": "attack"}],
            ),
        ]
    )
    await session.commit()
    await sign_in(client, "ash")
    for name in ("Kanto", "Johto"):
        team_id = await new_team(client, name)
        await client.put(f"/api/teams/{team_id}/members", json={"pokemon_ids": [25, 4]})

    # Act
    response = await client.get("/api/teams/alerts")

    # Assert — bulbasaur is not on my roster, charmander's event is 8 days old
    assert [alert["pokemon"]["name"] for alert in response.json()] == ["pikachu"]


@pytest.mark.parametrize(
    ("method", "path", "body"),
    [
        pytest.param("patch", "/api/teams/{id}", {"name": "mine now"}, id="rename"),
        pytest.param("delete", "/api/teams/{id}", None, id="delete"),
        pytest.param(
            "put", "/api/teams/{id}/members", {"pokemon_ids": []}, id="set-members"
        ),
    ],
)
async def test_another_users_team_is_not_found(client, method, path, body):
    # Arrange — ash owns a team, misty is signed in
    await sign_in(client, "ash")
    team_id = await new_team(client)
    await sign_in(client, "misty")

    # Act
    response = await client.request(method.upper(), path.format(id=team_id), json=body)

    # Assert — 404 rather than 403, which would confirm the id exists
    assert response.status_code == 404


async def test_deleting_a_team_removes_its_members(client, session):
    # Arrange
    session.add(make_pokemon(1, "bulbasaur", "grass"))
    await session.commit()
    await sign_in(client, "ash")
    team_id = await new_team(client)
    await client.put(f"/api/teams/{team_id}/members", json={"pokemon_ids": [1]})

    # Act
    response = await client.delete(f"/api/teams/{team_id}")

    # Assert — the cascade leaves no orphaned team_pokemon rows behind
    assert response.status_code == 204
    assert (await client.get("/api/teams")).json() == []
    assert await session.scalar(select(func.count()).select_from(TeamPokemon)) == 0


@pytest.mark.parametrize(
    "headers",
    [
        pytest.param({}, id="no-header"),
        pytest.param({"X-Admin-Secret": "guess"}, id="wrong-secret"),
    ],
)
async def test_sync_requires_the_admin_secret(client, headers):
    # Arrange — nothing; the guard runs before the handler

    # Act
    response = await client.post("/api/admin/sync", headers=headers)

    # Assert
    assert response.status_code == 401


async def test_sync_alerts_only_the_user_who_rostered_the_pokemon(client, pokeapi):
    # Arrange — seed pikachu through a sync, roster it as ash, then move it upstream
    pokeapi[25] = stub_pokemon_payload(25, "pikachu", ["electric"], attack=55)
    await client.post("/api/admin/sync", headers=ADMIN_HEADERS)
    await sign_in(client, "ash")
    team_id = await new_team(client)
    await client.put(f"/api/teams/{team_id}/members", json={"pokemon_ids": [25]})
    pokeapi[25] = stub_pokemon_payload(25, "pikachu", ["electric"], attack=60)

    # Act
    sync = await client.post("/api/admin/sync", headers=ADMIN_HEADERS)

    # Assert — ash is told, and a user with no pikachu is not
    assert sync.json()["alerted"] == 1
    assert [
        alert["pokemon"]["name"]
        for alert in (await client.get("/api/teams/alerts")).json()
    ] == ["pikachu"]
    await sign_in(client, "misty")
    assert (await client.get("/api/teams/alerts")).json() == []
