from datetime import datetime, timezone
import uuid
from sqlalchemy import ForeignKey, String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.db.models.base import Base
#from app.db.models.user import User
from app.db.models.enums import NotificationChannel, NotificationStatus

class Notification(Base):
    __tablename__ = "Notifications"
    title: Mapped[str | None] = mapped_column(String(), default=None)
    message: Mapped[str] = mapped_column(String())
    status: Mapped[NotificationStatus] = mapped_column(String(20), default=NotificationStatus.PENDING)
    channel: Mapped[NotificationChannel] = mapped_column(String(50))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    next_attempt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("Users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    user: Mapped["User"] = relationship("User", back_populates="notifications")
    
    