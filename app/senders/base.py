from typing import Protocol

from app.db.models.notification import Notification

class SenderProtocol(Protocol):
    async def send(self, notification: Notification) -> None:
        ...