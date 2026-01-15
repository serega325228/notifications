import uuid
import structlog

from app.db.models.enums import EventCategory, EventType, NotificationChannel
from app.services.notification_service import NotificationService
from app.notification_templates.registry import notification_templates
from app.services.user_service import UserService

log = structlog.get_logger(__name__)

class EventService:
    def __init__(
        self,
        *,
        user_service: UserService,
        notification_service: NotificationService
    ):
        self.__user_service = user_service
        self.__notification_service = notification_service
        self.__notification_templates = notification_templates

    async def handle_system_event(
        self, 
        event_type: EventType, 
        user_id: uuid.UUID,
        payload: dict
    ):
        log.info(
            "system_event_received",
            event_type=event_type,
            user_id=user_id
        )

        try:
            template = self.__notification_templates[event_type]()

        except KeyError: 
            log.error(
                "system_event_template_not_found",
                event_type=event_type
            )
            raise
        
        try:
            message = template.render(payload)

            await self.__user_service.update_last_active(user_id=user_id)

            await self.__notification_service.create_notification(
                user_id=user_id, 
                message=message, 
                channel=NotificationChannel.IN_APP
            )
            
            log.info(
                "system_event_notification_created",
                event_type=event_type,
                user_id=user_id,
                channel=NotificationChannel.IN_APP
            )

        except Exception:
            log.exception(
                "event_handling_failed",
                event_type=event_type,
                user_id=user_id
            )
            raise

    async def handle_custom_event(self, user_id: uuid.UUID, title: str, message: str, category: EventCategory):
        log.info(
            "customm_event_received",
            title=title,
            message=message,
            category=category
        )
        
        try:
            await self.__user_service.update_last_active(user_id=user_id)

            await self.__notification_service.create_for_category(
                title=title,
                message=message,
                channel=NotificationChannel.IN_APP,
                category=category
            )
            
            log.info(
                "custom_event_notification_created",
                title=title,
                message=message,
                category=category,
                channel=NotificationChannel.IN_APP
            )

        except Exception:
            log.exception(
                "custom_event_handling_failed",
                title=title,
                message=message,
                category=category,
            )
            raise