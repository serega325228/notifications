import uuid
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.db.models.base import Base
from app.db.models.notification import Notification
from app.db.models.user import User
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.services.notification_service import NotificationService
from app.db.models.enums import NotificationChannel, NotificationStatus
from unittest.mock import AsyncMock
from app.db.settings import settings
from app.services.user_service import UserService

@pytest.fixture
async def engine():
    engine = create_async_engine(
        settings.TEST_DATABASE_URL,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def session(engine):
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
def user_service(session):
    return UserService(
        user_repo=UserRepository(session=session)
    )

@pytest.fixture
def repository(session):
    return NotificationRepository(session=session)

@pytest.fixture
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
def sender():
    sender = AsyncMock()
    sender.send = AsyncMock(return_value=None)
    return sender

@pytest.fixture
def notification_factory():
    def factory(*, user_id: uuid.UUID, status: NotificationStatus = NotificationStatus.PENDING):
        return Notification(
            id=uuid.uuid4(),
            title="test_title",
            user_id=user_id,
            channel=NotificationChannel.IN_APP,
            status=status,
            attempts=0,
            message="test_message",
        )
    return factory

