import asyncio
from smtplib import SMTPRecipientsRefused

from app.errors.notification_error import FatalError, TemporaryError
from app.db.models.notification import Notification

class EmailSender:
    async def send(self, notification: Notification):
        try:
            await asyncio.sleep(1)
            print(f"[EMAIL] {notification.message}")
        except asyncio.TimeoutError:
            raise TemporaryError("SMTP timeout")
        except SMTPRecipientsRefused:
            raise FatalError("Invalid email")