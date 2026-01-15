import uuid
from fastapi import Request
from app.db.db import async_session_maker

from app.db.models.user import User
from app.repositories.user_repository import UserRepository

async def user_middleware(request: Request, call_next):
    user_id = request.cookies.get("user_id")

    response = await call_next(request)

    if user_id is None:
        user = User(id=uuid.uuid4())

        async with async_session_maker() as session:
            user_repo = UserRepository(session=session)

            await user_repo.create(user=user)
            
            response.set_cookie(
                key="user_id",
                value=str(user.id),
                max_age=60*60*24*365,
                samesite="lax",
                httponly=True,
                secure=False
            )

    return response