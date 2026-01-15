import uuid
import structlog
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select, update, func

from app.db.models.enums import NotificationStatus
from app.db.models.notification import Notification

log = structlog.get_logger(__name__)

class NotificationRepository:
    def __init__(self, *, session: AsyncSession):
        self.__session = session
    
    async def create(self, *, notification: Notification):
        try:
            self.__session.add(notification)
            await self.__session.flush()

        except SQLAlchemyError:
            log.exception(
                "db_create_notification_failed", 
                notification_id=notification.id
            )
            raise

    async def bulk_create(self, *, notifications: list[Notification]):
        try:
            self.__session.add_all(notifications)
            await self.__session.flush()

        except SQLAlchemyError:
            log.exception(
                "db_bulk_create_notifications_failed", 
            )
            raise

    async def get_by_id(self, *, id: uuid.UUID):
        query = select(Notification).filter_by(id=id)
        try:
            result = await self.__session.execute(query)
            return result.scalar_one()
        
        except SQLAlchemyError:
            log.exception(
                "db_get_notification_failed",
                notification_id=id
            )
            raise

    async def list_by_user(
        self, 
        *, 
        user_id: uuid.UUID, 
        status: NotificationStatus | None = None, 
        limit: int = 10
    ) -> list[Notification]:
        query = select(Notification).filter_by(user_id=user_id).limit(limit)
        
        if status is not None:
            query = query.filter_by(status=status)           
            
        try:
            result = await self.__session.execute(query)
            return list(result.scalars().all())
        
        except SQLAlchemyError:
            log.exception(
                "db_get_notifications_failed", 
                user_id=user_id
            )
            raise
    
    async def mark_status(self, *, notification_id: uuid.UUID, status: NotificationStatus):
        query = (
            update(Notification)
            .filter_by(id=notification_id)
            .values(
                status=status,
                updated_at=func.now()
            )
            .returning(Notification)
        )
        try:
            result = await self.__session.execute(query)
            return result.scalar_one()
        
        except SQLAlchemyError:
            log.exception(
                "db_mark_status_failed",
                notification_id=notification_id
            )
            raise
    
    async def update_attempts(self, *, notification_id: uuid.UUID, new_attempts: int, next_attempt_at: datetime):
        query = (
            update(Notification)
            .filter_by(id=notification_id)
            .values(
                attempts=new_attempts,
                next_attempt_at=next_attempt_at,
                updated_at=func.now()
            )
            .returning(Notification)
        )
        
        try:
            result = await self.__session.execute(query)
            return result.scalar_one()
        
        except SQLAlchemyError:
            log.exception(
                "db_update_attempts_failed",
                notification_id=notification_id
            )
            raise

    async def get_pending(self, *, limit: int = 10) -> list[Notification]:
        query = (
            select(Notification)
            .filter_by(status=NotificationStatus.PENDING)
            .with_for_update(skip_locked=True)
            .limit(limit)
        )

        try:
            result = await self.__session.execute(query)
            return list(result.scalars().all())
        
        except SQLAlchemyError:
            log.exception(
                "db_get_pending_failed"
            )
            raise
