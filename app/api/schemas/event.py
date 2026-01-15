from pydantic import BaseModel, ConfigDict

from app.db.models.enums import EventCategory, EventType

class SystemEventIn(BaseModel):
    type: EventType
    payload: dict

    model_config=ConfigDict(from_attributes=True)

class CustomEventIn(BaseModel):
    title: str
    message: str
    category: EventCategory

    model_config=ConfigDict(from_attributes=True)