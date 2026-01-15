import uuid
import structlog
from fastapi import APIRouter, Depends, Request

from app.api.dependencies import get_event_service
from app.api.schemas.event import CustomEventIn, SystemEventIn
from app.services.event_service import EventService

log = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/events", tags=["events"])

@router.post("/system")
async def handle_system_event(
    event: SystemEventIn,
    request: Request,
    service: EventService = Depends(get_event_service)
):
    user_id = uuid.UUID(request.cookies["user_id"])

    await service.handle_system_event(
        event_type=event.type,
        user_id=user_id, 
        payload=event.payload
    )
    log.info(
        "http_system_event_handle",
        event_type=event.type,
        user_id=user_id
    )
    return {"status": "ok"}

@router.post("/custom")
async def handle_custom_event(
    event: CustomEventIn,
    request: Request,
    service: EventService = Depends(get_event_service)
):
    user_id = uuid.UUID(request.cookies["user_id"])

    await service.handle_custom_event(
        user_id=user_id,
        title=event.title,
        message=event.message,
        category=event.category
    )
    log.info(
        "http_custom_event_handle",
        title=event.title,
        message=event.message,
        category=event.category
    )
    return {"status": "ok"}

