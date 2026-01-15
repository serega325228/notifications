import uuid
import structlog
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, update

from app.db.models.notification import Notification
from app.db.models.user import User

log = structlog.get_logger(__name__)

class UserRepository:
    def __init__(self, *, session: AsyncSession):
        self.__session = session
    
    async def create(self, *, user: User):
        try:
            self.__session.add(user)
            await self.__session.commit()
        except SQLAlchemyError:
            log.exception(
                "db_create_user_failed", 
                user_id=user.id
            )
            raise

    async def get_by_id(self, *, id: uuid.UUID) -> User:
        query = select(User).filter_by(id=id)
        try:
            result = await self.__session.execute(query)
            return result.scalar_one()
        
        except SQLAlchemyError:
            log.exception(
                "db_get_user_failed",
                user_id=id
            )
            raise

    async def get_active_users(self, *, last_active: datetime) -> list[User]:
        query = (
            select(User)
            .where(User.last_active>last_active)
        )

        try:
            result = await self.__session.execute(query)
            return list(result.scalars().all())
        
        except SQLAlchemyError:
            log.exception(
                "db_get_active_users_failed"
            )
            raise

    async def update_last_active(self, *, user_id: uuid.UUID):
        query = (
            update(User)
            .filter_by(id=user_id)
            .values(last_active=func.now())
        )

        try:
            await self.__session.execute(query)
        
        except SQLAlchemyError:
            log.exception(
                "db_update_last_active_failed"
            )
            raise
