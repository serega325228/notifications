import uuid
from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.repositories.user_repository import UserRepository
from app.senders.registry import SENDERS
from app.services.user_service import UserService

from ..db.db import async_session_maker
from app.services.event_service import EventService
from app.services.notification_service import NotificationService
from app.repositories.notification_repository import NotificationRepository

log = structlog.get_logger(__name__)

async def get_async_session():
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def get_user_service(
    session: AsyncSession = Depends(get_async_session)
):
    return UserService(user_repo=UserRepository(session=session))

async def get_notification_service(
    session: AsyncSession = Depends(get_async_session),
    user_service: UserService = Depends(get_user_service)
):
    return NotificationService(
        notification_repo=NotificationRepository(session=session),
        user_service=user_service,
        senders=SENDERS
    )

async def get_event_service(
    user_service: UserService = Depends(get_user_service),
    notification_service: NotificationService = Depends(get_notification_service)                  
):
    return EventService(
        user_service=user_service,
        notification_service=notification_service
    )

async def get_user_id(
    user_id: uuid.UUID | None = Cookie(defult=None)
) -> uuid.UUID:
    if not user_id:
        raise HTTPException(401, "User not identified")
    return user_id

