import asyncio

from app.errors.notification_error import FatalError, TemporaryError
from app.db.models.notification import Notification

class InAppSender:
    async def send(self, notification: Notification):
        try:
            await asyncio.sleep(1)
            print(f"[IN-APP] {notification.message}")
        except asyncio.TimeoutError:
            raise TemporaryError("sending timeout")
        except Exception:
            raise FatalError("pass")