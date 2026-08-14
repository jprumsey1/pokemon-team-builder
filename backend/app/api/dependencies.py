"""Injectable dependencies shared by the routes."""

import secrets
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import session_factory
from app.models import User


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with session_factory() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(request: Request, db: SessionDep) -> User:
    """The signed-in user, or 401. The cookie is signed by SessionMiddleware, not encrypted."""
    user_id = request.session.get("user_id")
    user = await db.get(User, user_id) if user_id else None
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not signed in")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_admin(x_admin_secret: Annotated[str, Header()] = "") -> None:
    # compare_digest rather than ==, so a wrong secret can't be found a byte at a time.
    if not secrets.compare_digest(x_admin_secret, settings.admin_secret):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Bad admin secret")
