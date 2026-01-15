from collections.abc import Callable
import uuid
import structlog
import json
from datetime import timezone, datetime, timedelta

from app.errors.notification_error import FatalError, NotificationError, TemporaryError
from app.errors.user_error import UserError
from app.senders.base import SenderProtocol
from app.senders.registry import SENDERS
from app.repositories.notification_repository import NotificationRepository
from app.db.models.enums import EventCategory, NotificationChannel, NotificationStatus
from app.db.models.notification import Notification
from app.services.user_service import UserService

log = structlog.get_logger(__name__)

SenderFactory = Callable[[], SenderProtocol]

class NotificationService:
    MAX_ATTEMPTS = 5
    DELAY = 3

    def __init__(
            self, 
            *, 
            notification_repo: NotificationRepository,
            user_service: UserService,
            senders: dict[NotificationChannel, SenderFactory] | None = None,
        ):
        self.__repo = notification_repo
        self.__user_service = user_service
        self.__senders = senders or SENDERS

    async def process_sending(self, *, notification: Notification):
        attempts = notification.attempts + 1

        next_attempt_at = datetime.now(timezone.utc) + timedelta(seconds=self.DELAY)

        await self.__repo.update_attempts(
            notification_id=notification.id, 
            new_attempts=attempts,
            next_attempt_at=next_attempt_at
        )

        log.info(
            "notification_sending_attempt",
            notification_id=notification.id,
            attempt=attempts,
            channel=notification.channel
        )

        sender = self.__senders[notification.channel]()

        try:
            log.info(
                "notification_sending",
                notification_id=notification.id
            )
            await sender.send(notification)
            await self.mark_as_sent(notification_id=notification.id)

        except TemporaryError as e:
            await self._handle_retry(
                notification=notification, 
                attempts=attempts, 
                error=e
            )
            
        except FatalError as e:
            await self._handle_failure(
                notification=notification, 
                attempts=attempts, 
                error=e
            )

    async def _handle_retry(
            self, *, 
            notification: Notification, 
            attempts: int, 
            error: Exception
        ):
        if attempts >= self.MAX_ATTEMPTS:
            await self.mark_as_failed(notification_id=notification.id)

            log.error(
                "notification_failed_max_attempts",
                notification_id=notification.id,
                attempts=attempts
            )
            return
        
        await self.mark_as_pending(notification_id=notification.id)

        log.warning(
            "notification_retry_scheduled",
            notification_id=notification.id,
            attempt=attempts,
            reason=str(error)
        )

    async def _handle_failure(
        self,
        notification: Notification,
        attempts: int,
        error: Exception,
    ):
        await self.mark_as_failed(notification_id=notification.id)

        log.error(
            "notification_failed",
            notification_id=notification.id,
            channel=notification.channel,
            attempts=attempts,
            reason=str(error),
        )

    async def get_processing(self, *, limit: int = 10) -> list[Notification]:
        try:
            notifications = await self.__repo.get_pending(limit=limit)

            for n in notifications:
                log.info(
                    "notification_get_processing",
                    notification_id=n.id
                )
                await self.mark_as_processing(notification_id=n.id)
        
            return notifications
        
        except NotificationError:
            log.exception(
                "notification_get_processing_failed",
            )
            raise

    async def mark_as_read(self, *, notification_id: uuid.UUID, user_id: uuid.UUID):
        try:
            notification = await self.__repo.get_by_id(id=notification_id)

            if notification.user_id != user_id:
                log.warning(
                    "notification_mark_read_forbidden",
                    notification_id=notification_id,
                    user_id=user_id,
                    owner_id=notification.user_id
                )
                raise PermissionError("Permission denied")

            if notification.status != NotificationStatus.SENT:
                log.warning(
                    "notification_mark_read_invalid_status",
                    notification_id=notification_id,
                    current_status=notification.status
                )
                raise ValueError("Cannot mark undread notification")
            
            await self.__repo.mark_status(notification_id=notification_id, status=NotificationStatus.READ)
            log.info(
                "notification_marked_as_read",
                notification_id=notification_id,
                user_id=user_id
            )

        except NotificationError:
            log.exception(
                "notification_mark_as_read_failed",
                notification_id=notification_id,
                user_id=user_id
            )
            raise

    async def mark_as_sent(self, *, notification_id: uuid.UUID):
        try:
            notification = await self.__repo.get_by_id(id=notification_id)

            if notification.status != NotificationStatus.PROCESSING:
                log.warning(
                    "notification_mark_sent_invalid_status",
                    notification_id=notification_id,
                    current_status=notification.status
                )
                raise ValueError("Cannot mark a notification that isn't processing")

            await self.__repo.mark_status(notification_id=notification_id, status=NotificationStatus.SENT)
            log.info(
                "notification_marked_as_sent",
                notification_id=notification_id
            )

        except NotificationError:
            log.exception(
                "notification_mark_as_sent_failed",
                notification_id=notification_id
            )
            raise

    async def mark_as_pending(self, *, notification_id: uuid.UUID):
        try:
            notification = await self.__repo.get_by_id(id=notification_id)

            if notification.status != NotificationStatus.PROCESSING:
                log.warning(
                    "notification_mark_pending_invalid_status",
                    notification_id=notification_id,
                    current_status=notification.status
                )
                raise ValueError("Cannot mark a notification that isn't processing")
            
            await self.__repo.mark_status(notification_id=notification_id, status=NotificationStatus.PENDING)
            log.info(
                "notification_marked_as_pending",
                notification_id=notification_id
            )

        except NotificationError:
            log.exception(
                "notification_mark_as_pending_failed",
                notification_id=notification_id
            )
            raise

    async def mark_as_failed(self, *, notification_id: uuid.UUID):
        try:
            notification = await self.__repo.get_by_id(id=notification_id)

            if notification.status != NotificationStatus.PROCESSING:
                log.warning(
                    "notification_mark_failed_invalid_status",
                    notification_id=notification_id,
                    current_status=notification.status
                )
                raise ValueError("Cannot mark a notification that isn't processing")
            
            await self.__repo.mark_status(notification_id=notification_id, status=NotificationStatus.FAILED) 
            log.info(
                "notification_marked_as_pending",
                notification_id=notification_id
            )

        except NotificationError:
            log.exception(
                "notification_mark_as_failed_error",
                notification_id=notification_id
            )
            raise

    async def mark_as_processing(self, *, notification_id: uuid.UUID):
        try:
            notification = await self.__repo.get_by_id(id=notification_id)

            if notification.status != NotificationStatus.PENDING:
                log.warning(
                    "notification_mark_processing_invalid_status",
                    notification_id=notification_id,
                    current_status=notification.status
                )
                raise ValueError("Cannot mark a notification that isn't pending")
            
            await self.__repo.mark_status(notification_id=notification_id, status=NotificationStatus.PROCESSING)
            log.info(
                "notification_marked_as_processing",
                notification_id=notification_id
            )

        except NotificationError:
            log.exception(
                "notification_mark_as_processing_failed",
                notification_id=notification_id
            )
            raise

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
        
        except NotificationError:
            log.exception(
                "notification_get_by_id_failed",
                notification_id=notification_id
            )
            raise IndexError("Notification id doesn't exist")

    async def get_sent(self, *, user_id: uuid.UUID) -> list[Notification]:
        try:
            notifications = await self.__repo.list_by_user(user_id=user_id, status=NotificationStatus.SENT, limit=100)
            log.info(
                "get_sent_by_user",
                user_id=user_id
            )
            return list(notifications)
        
        except Exception:
            log.exception(
                "get_sent_by_user_failed",
                user_id=user_id
            )
            raise IndexError("User id doesn't exist")

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

    def sse_data(self, *, data: dict) -> str:
        return f"data: {json.dumps(data, ensure_ascii=False)}"

    async def create_for_category(
        self,
        *,
        title: str,
        message: str,
        category: EventCategory,
        channel: NotificationChannel
    ):
        if category == EventCategory.GENERAL:
            try:
                users = await self.__user_service.get_all_active()

                notifications = [
                    Notification(
                        user_id=user.id,
                        title=title,
                        message=message,
                        channel=channel,
                        status=NotificationStatus.PENDING
                    )
                    for user in users
                ]

                await self.__repo.bulk_create(notifications=notifications)

                log.info(
                    "notifications_create_for_category",
                    title=title,
                    message=message,
                    channel=channel,
                    category=category
                )

            except NotificationError:
                log.exception(
                    "notification_create_for_category_failed",
                    title=title,
                    message=message,
                    channel=channel,
                    category=category
                )
                raise

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
        
        except NotificationError:
            log.exception(
                "notification_create_failed",
                user_id=notification.user_id,
                title=notification.title,
                message=notification.message,
                channel=notification.channel,
                status=notification.status
            )
            raise