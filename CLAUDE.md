# Pokémon Team Builder

FastAPI + SQLAlchemy 2.0 async + Postgres (`backend/`), React 19 + Vite + Tailwind v4
(`frontend/`). Setup and run commands live in `README.md` — read it, don't edit it.

## Checks

Before claiming work is done, from `backend/`:

```bash
uv run ruff check . && uv run ruff format . && uv run pyright && uv run pytest
```

`.githooks/pre-commit` gates commits on the first three. Tests need `docker compose up -d`.
Frontend: `npm run lint` (oxlint) and `npm run build` from `frontend/`.

## README

Don't add to the README.md unless asked. This is technical documentation meant to be written by a human.

## Comments

**Explain why, not what, in one or two lines.**

Write a comment only when the code is surprising in a non-obvious way.
Do not restate what the line does, and do not put high-level design rationale in source.

This belongs in plan documents and finalized overview in `README.md`.

## Code Style

Names corresponding to the same domain entity or operation should be consistent. I.e. `sync_pokemon` and `update_pokemon` should be named the same thing if they represent same operation.

Follow the "you aren't gonna need it principle" - don't introduce something new unless we are using it in the feature that's being worked on.

## API

During development and design, defer to standards and suggestions from FastAPI docs https://fastapi.tiangolo.com/.

## Database

Alembic owns the schema. Edit `backend/app/models.py`, but do not run
`alembic revision --autogenerate` — let the user do it.

## Tests

Follow "arrange, act, assert" when writing tests with pytest. One python function = one test case with a readable name. 

`asyncio_mode = "auto"` is required — without it async tests silently skip rather than fail.
Sync integration tests use a separate `ptb_test` database.

Tests for front-end aren't necessary right now.