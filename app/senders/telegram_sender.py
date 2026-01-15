import asyncio

from app.db.models.notification import Notification

class TelegramSender:
    async def send(self, notification: Notification):
        await asyncio.sleep(1)
        print(f"[TG] Send to user {notification.user_id}: {notification.message}")