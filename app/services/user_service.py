import uuid
import structlog
from datetime import timezone, datetime, timedelta

from app.db.models.user import User
from app.errors.user_error import UserError
from app.repositories.user_repository import UserRepository

log = structlog.get_logger(__name__)

class UserService:
    DELAY = 5

    def __init__(
            self, 
            *, 
            user_repo: UserRepository,
        ):
        self.__repo = user_repo

    async def create_user(self):
        user = User()
        try:
            await self.__repo.create(user=user)
            log.info(
                "user_create",
                id=user.id,
                created_at=user.created_at
            )
            return user
        
        except UserError:
            log.exception(
                "user_create_failed",
                id=user.id,
                created_at=user.created_at
            )
            raise

    async def get_all_active(self) -> list[User]:

        last_active = datetime.now(timezone.utc) - timedelta(weeks=self.DELAY)

        try:
            return await self.__repo.get_active_users(last_active=last_active)
                
        except UserError:
            log.exception(
                "user_get_all_active_failed",
            )
            raise

    async def update_last_active(self, *, user_id: uuid.UUID):
        try:
            await self.__repo.update_last_active(user_id=user_id)
            
        except UserError:
            log.exception(
                "user_update_last_active_failed",
                user_id=user_id
            )
            raise

    '''  
    async def notification_by_id(self, *, notification_id: uuid.UUID, user_id: uuid.UUID) -> Notification:
        try:
            notification = await self.__repo.get_by_id(id=notification_id)

            if notification.user_id != user_id:
                log.warning(
                    "notification_get_by_id_forbidden",
                    notification_id=notification_id,
                    user_id=user_id,
                    owner_id=notification.user_id
                )
                raise PermissionError("Permission denied")
            
            log.info(
                "notification_get_by_id",
                notification_id=notification_id
            )
            return notification
        
        except UserError:
            log.exception(
                "notification_get_by_id_failed",
                notification_id=notification_id
            )
            raise IndexError("Notification id doesn't exist")

    async def notifications_by_user(self, *, user_id: uuid.UUID, status: NotificationStatus | None = None, limit: int = 10) -> list[Notification]:
        try:
            notifications = await self.__repo.list_by_user(user_id=user_id, status=status, limit=limit)
            log.info(
                "notifications_get_by_user",
                user_id=user_id
            )
            return list(notifications)
        
        except Exception:
            log.exception(
                "notifications_get_by_user_failed",
                user_id=user_id
            )
            raise IndexError("User id doesn't exist")

    async def create_notification(
            self, 
            *,
            user_id: uuid.UUID,
            title: str | None = None,
            message: str,
            channel: NotificationChannel
        ) -> Notification:
        notification = Notification(
            user_id = user_id,
            title=title,
            message = message,
            channel = channel,
            status = NotificationStatus.PENDING
        )
        try:
            await self.__repo.create(notification=notification)
            log.info(
                "notification_create",
                user_id=notification.user_id,
                title=notification.title,
                message=notification.message,
                channel=notification.channel,
                status=notification.status
            )
            return notification
        
        except UserError:
            log.exception(
                "notification_create_failed",
                user_id=notification.user_id,
                title=notification.title,
                message=notification.message,
                channel=notification.channel,
                status=notification.status
            )
            raise
    '''