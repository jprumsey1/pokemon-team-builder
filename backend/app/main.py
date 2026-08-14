from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    yield
    await engine.dispose()


app = FastAPI(title="Pokémon Team Builder", lifespan=lifespan)


@app.get("/api/health")
async def health(db: Annotated[AsyncSession, Depends(get_db)]) -> dict[str, str]:
    """Liveness + database reachability."""
    await db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}
