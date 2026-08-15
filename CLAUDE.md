# Pokémon Team Builder

## Comments

**Explain why, not what, in one or two lines.**

Write a comment only when the code is surprising in a non-obvious way.
Do not restate what the line does, and do not put high-level design rationale in source.

This belongs in plan documents and finalized overview in `README.md`.

## Code Style

Names corresponding to the same domain entity or operation should be consistent. 
I.e. `sync_pokemon` and `update_pokemon` should be named the same thing if they are the 
same operation.

## README

Don't add to the README.md unless asked. This is technical documentation meant to be written by a human.

## API

During development and design, defer to standards and suggestions from FastAPI docs https://fastapi.tiangolo.com/.

## Database

Alembic is used for schema migrations in `backend/app/models.py`. Do not run schema generations, let the user do it. 

## Tests

Follow "arrange, act, assert" when writing tests. One python function = one test case with a readable name. 
