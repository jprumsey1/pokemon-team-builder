# Pokémon Team Builder

## Background Sync Job

TODO

## Local Development

This app can be run **(A)** fully in containers or **(B)** with FastAPI and Vite dev servers running on the host.

### Requirements
- Docker or equivalent

If running outside containers:
- [uv](https://docs.astral.sh/uv/)
- Node

### First-time setup

`./setup.sh` applies DB migrations, seeds the type matchups and Pokémon data from PokéAPI, then tears down containers.

These datasets rarely change and re-running is safe (will just request resources from PokéAPI again). Normally, the Pokémon data sync portion runs as a scheduled background job (see [Background Sync Job](#background-sync-job))

You can run the equivalent against a running API as well, which is how data gets seeded data in production.

```bash
curl -X POST -H "X-Admin-Secret: dev-admin-secret" localhost:8000/api/admin/sync-type-matchup
curl -X POST -H "X-Admin-Secret: dev-admin-secret" localhost:8000/api/admin/sync
```

### Startup

**A.** Everything in containers
```bash
docker compose --profile container up -d --build
docker compose --profile container down   # stop
```

or 

**B.** API and frontend on the host, DB in a container

```bash
docker compose up -d
cd backend && uv sync && uv run fastapi dev app/main.py   # :8000
cd frontend && npm install && npm run dev                 # :5173
docker compose down                       # stop
```

### Tests

```bash
cd backend && uv run pytest
```

Integration tests need the database container running and use their own `ptb_test` database. The rest are pure unit tests.

### Database migrations

[Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html) owns the schema and migrations are applied manually locally.

After editing `models.py`:

```bash
cd backend
uv run alembic revision --autogenerate -m "<Message>"
# Read and verify migration script!
uv run alembic upgrade head
```
