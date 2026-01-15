import asyncio
import uuid
from fastapi.responses import StreamingResponse
import structlog
from fastapi import APIRouter, Depends, Request

from app.api.dependencies import get_notification_service, get_user_id
from app.api.schemas.notification import NotificationOut
from app.services.notification_service import NotificationService

log = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@router.get("/stream")
async def stream(
    request: Request,
    user_id: uuid.UUID = Depends(get_user_id),
    service: NotificationService = Depends(get_notification_service)
):
    async def gen():
        try:
            while True:
                if await request.is_disconnected():
                    break

                notifications = await service.get_sent(user_id=user_id)

                for n in notifications:
                    payload = {
                        "id": str(n.id),
                        "title": n.title,
                        "message": n.message,
                        "created_at": n.created_at.isoformat(),
                    }

                    yield service.sse_data(data=payload)

                await asyncio.sleep(1)

        except asyncio.CancelledError:
            pass

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

@router.get("/inapp")
async def inapp(
    user_id: uuid.UUID = Depends(get_user_id),
    service: NotificationService = Depends(get_notification_service)
):
    return await service.get_sent(user_id=user_id)

@router.post("/{notification_id}/read")
async def mark_read(
    notification_id: uuid.UUID,
    user_id: uuid.UUID = Depends(get_user_id),
    service: NotificationService = Depends(get_notification_service)
):
    await service.mark_as_read(notification_id=notification_id, user_id=user_id)
    log.info(
        "http_notification_mark_read",
        user_id=user_id,
        notification_id=notification_id
    )
    return {"status": "ok"}

@router.get("/{notification_id}", response_model=NotificationOut)
async def get_by_id(
    notification_id: uuid.UUID,
    user_id: uuid.UUID,
    service: NotificationService = Depends(get_notification_service)
):
    log.info(
        "http_notification_get_by_id",
        notification_id=notification_id,
        user_id=user_id
    )
    return await service.notification_by_id(notification_id=notification_id, user_id=user_id)

@router.get("/{user_id}", response_model=list[NotificationOut])
async def list_by_user(
    user_id: uuid.UUID,
    limit: int = 20,
    service: NotificationService = Depends(get_notification_service)
):
    log.info(
        "http_notifications_get_by_user",
        user_id=user_id
    )
    return await service.notifications_by_user(user_id=user_id, limit=limit)





    