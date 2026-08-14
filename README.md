# Pokémon Team Builder

## Development

### Run locally with debugging

Postgres runs in a container; the API runs on the host so IDE can own process and debug.

```bash
docker compose up -d  # starts DB only
cd backend && uv sync && uv run alembic upgrade head # run DB migrations
```

To stop it:

```bash
docker compose down
```

### Running with the API in a container

The `api` service is behind a Compose profile called `container`, so a plain `docker compose up -d` never starts it. That
keeps port 8000 free for the debugger. Below will run all components in containers:

```bash
docker compose --profile container up -d --build # builds images, starts all containers
docker compose run --rm api alembic upgrade head # run DB migrations
```

To stop it:

```bash
docker compose --profile container down
```

### Database migrations

[Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html) owns the schema and DB migrations should be applied on app startup.

After editing `models.py`:

```bash
cd backend
uv run alembic revision --autogenerate -m "<Message>"
# Read and verify migration script!
uv run alembic upgrade head
```
