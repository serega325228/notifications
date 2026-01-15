import pytest
import uuid
from unittest.mock import AsyncMock, Mock

from app.db.models.user import User
from app.services.notification_service import NotificationService
from app.db.models.notification import Notification
from app.db.models.enums import NotificationChannel, NotificationStatus

@pytest.fixture()
def repository(notification):
    repo = Mock()

    repo.get_by_id = AsyncMock(return_value=notification)
    repo.update_attempts = AsyncMock()
    repo.get_pending = AsyncMock()
    repo.mark_status = AsyncMock()
    repo.create = AsyncMock()

    return repo

@pytest.fixture()
def user():
    return User(
        id=uuid.uuid4(),

    )

@pytest.fixture()
def user_service(user):
    user_service = Mock()

    user_service.get_all_active = AsyncMock(return_value=[user for _ in range(10)])

    return user_service

@pytest.fixture
def sender():
    sender = Mock()
    sender.send = AsyncMock(return_value=None)
    return sender

@pytest.fixture()
def service(repository, user_service, sender):
    senders = {
        NotificationChannel.IN_APP: lambda: sender
    }

    return NotificationService(
        notification_repo=repository,
        user_service=user_service,
        senders=senders,
    )

@pytest.fixture
def notification():
    n = Notification(
        id=uuid.uuid4(),
        title="test_title",
        user_id=uuid.uuid4(),
        channel=NotificationChannel.IN_APP,
        status=NotificationStatus.PENDING,
        attempts=0,
        message="test_message",
    )
    return n

@pytest.fixture
def notifications(notification):
    return [notification for _ in range(10)]
