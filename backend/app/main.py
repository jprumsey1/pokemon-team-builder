from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.db import engine
from app.scheduler import build_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    scheduler = build_scheduler()
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)
    await engine.dispose()


app = FastAPI(title="Pokémon Team Builder", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret)
app.include_router(api_router, prefix="/api")

# Last: a mount at "/" matches every path, and Starlette takes the first match — registered
# above the router it would swallow /api. Absent until `npm run build`, so don't crash dev.
static = Path(__file__).parent / "static"
if static.is_dir():
    app.mount("/", StaticFiles(directory=static, html=True), name="ui")
