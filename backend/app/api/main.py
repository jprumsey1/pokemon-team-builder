"""Assembles every route under one router, which app.main mounts at /api."""

from fastapi import APIRouter, Depends

from app.api.dependencies import require_admin
from app.api.routes import admin, pokemon, session, teams

api_router = APIRouter()
api_router.include_router(session.router, prefix="/session")
api_router.include_router(pokemon.router, prefix="/pokemon")
api_router.include_router(teams.router)
api_router.include_router(
    admin.router, prefix="/admin", dependencies=[Depends(require_admin)]
)
