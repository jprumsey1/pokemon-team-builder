# Pokémon Team Builder

FastAPI + SQLAlchemy 2.0 async + Postgres (`backend/`), React 19 + Vite + Tailwind v4
(`frontend/`).

## Checks

Before claiming work is done, from `backend/`:

```bash
uv run ruff check . && uv run ruff format . && uv run pyright && uv run pytest
```

Frontend: `npm run lint` (oxlint) and `npm run build` (runs `tsc -b`) from `frontend/`.
Tests for the frontend aren't necessary right now.

## README

Don't add to the README.md unless asked. This is technical documentation meant to be written by a human.

## Comments

**Use sparingly - only to explain why, not what, in one or two lines.**

Write a comment only when the code is non-obvious.
Do not just restate what the line does. 

Do not put high-level design rationale in source. This belongs in plan documents and finalized overview in `README.md`.

## Code Style

Names corresponding to the same domain entity or operation should be consistent. I.e. `sync_pokemon` and `update_pokemon` should be named the same thing if they represent same operation.

Follow the "you aren't gonna need it principle" - don't introduce something new unless we are using it in the feature that's being worked on.

Use "rule of three" when introducing a new function. If similar code is used three or more times, extract it.

## Database

Alembic owns the schema. Edit `backend/app/models.py`, but do not run
`alembic revision --autogenerate` — let the user do it.

## Tests

Backend tests need `docker compose up -d` to ensure the db container is running.

Follow "arrange, act, assert". One python function = one test case with a readable name.

`asyncio_mode = "auto"` is required — without it async tests silently skip rather than fail.
Sync integration tests use a separate `ptb_test` database.
