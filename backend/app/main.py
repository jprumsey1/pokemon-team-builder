from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.api.main import api_router
from app.config import settings
from app.db import engine
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

static = Path(__file__).parent / "static"
if static.is_dir():
    # Prod/container only: serves static files from root URL
    # local front end can be run outside of this setup with `npm run dev`
    app.mount("/", StaticFiles(directory=static, html=True))
