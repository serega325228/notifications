from app.db.models.enums import NotificationChannel
from app.senders.email_sender import EmailSender
from app.senders.inapp_sender import InAppSender
from app.senders.telegram_sender import TelegramSender


SENDERS = {
    NotificationChannel.IN_APP: InAppSender,
    NotificationChannel.TELEGRAM: TelegramSender,
    NotificationChannel.EMAIL: EmailSender,
}