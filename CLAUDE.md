# Pokémon Team Builder

## Comments

**Explain why, not what, in one or two lines.**

Write a comment only when the code is surprising and the surprise isn't
recoverable by reading it. Do not restate what the line does, and do not put high-level design rationale in source.
This belongs in plan documents and finalized overview in `README.md`.

## README

Don't add to the README.md unless asked. This is technical documentation meant to be written by hand.

## API

During development and design, defer to standards and suggestions from https://fastapi.tiangolo.com/

## Database

Alembic is used for schema migrations in `backend/app/models.py`.

```bash
uv run alembic revision --autogenerate -m "..."   # after editing models.py
uv run alembic upgrade head
```

Read the generated migration before applying it. Autogenerate cannot detect a
rename: it emits drop + add, which discards the column's data.

## Running locally

```bash
docker compose up -d db
cd backend && uv sync && uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```
