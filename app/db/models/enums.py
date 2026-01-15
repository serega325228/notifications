from enum import Enum

class NotificationChannel(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    TELEGRAM = "telegram"

class EventType(str, Enum):
    USER_REGISTERED = "user_registered"
    ORDER_PAID = "order_paid"
    ORDER_CANCELLED = "order_cancelled"

class EventCategory(str, Enum):
    GENERAL = "general"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"
