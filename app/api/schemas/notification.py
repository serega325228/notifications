import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.db.models.enums import NotificationChannel, NotificationStatus

class NotificationOut(BaseModel):
    id: uuid.UUID
    title: str | None
    channel: NotificationChannel
    message: str    
    status: NotificationStatus
    created_at: datetime

    model_config=ConfigDict(from_attributes=True)
    