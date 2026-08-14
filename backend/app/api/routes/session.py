"""Sign in and sign out based on username and session cookie."""

from fastapi import APIRouter, Request, Response, status
from sqlalchemy import select

from app.api.dependencies import CurrentUser, SessionDep
from app.models import User
from app.schemas import SessionIn, UserOut

router = APIRouter(tags=["session"])


@router.post("")
async def sign_in(body: SessionIn, request: Request, db: SessionDep) -> UserOut:
    """Create the user if absent, then set the session cookie."""
    user = await db.scalar(select(User).where(User.username == body.username))
    if user is None:
        user = User(username=body.username)
        db.add(user)
        await db.commit()
    request.session["user_id"] = user.id
    return UserOut.model_validate(user)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def sign_out(request: Request) -> Response:
    request.session.clear()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me")
async def me(user: CurrentUser) -> UserOut:
    return UserOut.model_validate(user)
