import uuid
import pytest
from unittest.mock import AsyncMock
from app.db.models.enums import NotificationChannel, NotificationStatus
from app.errors.notification_error import FatalError, TemporaryError


@pytest.mark.parametrize(
    "initial_attempts, sender_error, expected_status, expected_attempts",
    [
        (0, None, NotificationStatus.SENT, 1),
        (0, TemporaryError("temp"), NotificationStatus.PENDING, 1),
        (4, TemporaryError("temp"), NotificationStatus.FAILED, 5),
        (0, FatalError("fatal"), NotificationStatus.FAILED, 1),
    ]
)
async def test_process_sending(
    service,
    repository,
    sender,
    notification,
    initial_attempts,
    sender_error,
    expected_status,
    expected_attempts,
):
    notification.attempts = initial_attempts
    notification.status = NotificationStatus.PROCESSING

    if sender_error:
        sender.send = AsyncMock(side_effect=sender_error)
    else:
        sender.send = AsyncMock(return_value=None)

    await service.process_sending(notification=notification)

    repository.update_attempts.assert_awaited_once()

    if expected_status == NotificationStatus.SENT:
        repository.mark_status.assert_awaited_with(
            notification_id=notification.id,
            status=NotificationStatus.SENT
        )
    elif expected_status == NotificationStatus.PENDING:
        repository.mark_status.assert_awaited_with(
            notification_id=notification.id,
            status=NotificationStatus.PENDING
        )
    else:
        repository.mark_status.assert_awaited_with(
            notification_id=notification.id,
            status=NotificationStatus.FAILED
        )

    assert notification.attempts + 1 == expected_attempts

async def test_get_processing(
    service,
    repository,
    notifications
):
    repository.get_pending = AsyncMock(return_value=notifications)

    service.mark_as_processing = AsyncMock()

    await service.get_processing(limit=10)

    repository.get_pending.assert_awaited_once_with(limit=10)

    assert service.mark_as_processing.await_count == len(notifications)

    service.mark_as_processing.assert_any_await(
        notification_id=notifications[0].id
    )

@pytest.mark.parametrize(
    "initial_status, expect_error", 
    [
        (NotificationStatus.PENDING, False), 
        (NotificationStatus.READ, True)
    ]
)
async def test_mark_as_processing(
    service,
    repository,
    notification,
    initial_status,
    expect_error
):
    notification.status = initial_status

    if expect_error:
        with pytest.raises(ValueError):
            await service.mark_as_processing(notification_id=notification.id)

        repository.mark_status.assert_not_awaited()

    else:
        await service.mark_as_processing(notification_id=notification.id)

        repository.get_by_id.assert_awaited_once_with(id=notification.id)

        repository.mark_status.assert_awaited_once_with(
            notification_id=notification.id,
            status=NotificationStatus.PROCESSING
        )

@pytest.mark.parametrize(
    "initial_status, expect_error", 
    [
        (NotificationStatus.PROCESSING, False), 
        (NotificationStatus.PENDING, True)
    ]
)
async def test_mark_as_sent(
    service,
    repository,
    notification,
    initial_status,
    expect_error
):
    notification.status = initial_status

    if expect_error:
        with pytest.raises(ValueError):
            await service.mark_as_sent(notification_id=notification.id)

        repository.mark_status.assert_not_awaited()

    else:
        await service.mark_as_sent(notification_id=notification.id)

        repository.get_by_id.assert_awaited_once_with(id=notification.id)

        repository.mark_status.assert_awaited_once_with(
            notification_id=notification.id,
            status=NotificationStatus.SENT
        )

@pytest.mark.parametrize(
    "initial_status, expect_error", 
    [
        (NotificationStatus.PROCESSING, False), 
        (NotificationStatus.PENDING, True)
    ]
)
async def test_mark_as_failed(
    service,
    repository,
    notification,
    initial_status,
    expect_error
):
    notification.status = initial_status

    if expect_error:
        with pytest.raises(ValueError):
            await service.mark_as_failed(notification_id=notification.id)

        repository.mark_status.assert_not_awaited()

    else:
        await service.mark_as_failed(notification_id=notification.id)

        repository.get_by_id.assert_awaited_once_with(id=notification.id)

        repository.mark_status.assert_awaited_once_with(
            notification_id=notification.id,
            status=NotificationStatus.FAILED
        )

@pytest.mark.parametrize(
    "initial_status, expect_error", 
    [
        (NotificationStatus.PROCESSING, False), 
        (NotificationStatus.PENDING, True)
    ]
)
async def test_mark_as_pending(
    service,
    repository,
    notification,
    initial_status,
    expect_error
):
    notification.status = initial_status

    if expect_error:
        with pytest.raises(ValueError):
            await service.mark_as_pending(notification_id=notification.id)

        repository.mark_status.assert_not_awaited()

    else:
        await service.mark_as_pending(notification_id=notification.id)

        repository.get_by_id.assert_awaited_once_with(id=notification.id)

        repository.mark_status.assert_awaited_once_with(
            notification_id=notification.id,
            status=NotificationStatus.PENDING
        )

@pytest.mark.parametrize(
    "initial_status, expected_error", 
    [
        (NotificationStatus.SENT, None),
        (NotificationStatus.SENT, PermissionError),
        (NotificationStatus.PENDING, ValueError),
    ]
)
async def test_mark_as_read(
    service,
    repository,
    notification,
    initial_status,
    expected_error
):
    notification.status = initial_status

    if expected_error:
        with pytest.raises(expected_error):
            if expected_error == PermissionError:
                await service.mark_as_read(notification_id=notification.id, user_id=uuid.uuid4())
            else:
                await service.mark_as_read(notification_id=notification.id, user_id=notification.user_id)

        repository.mark_status.assert_not_awaited()

    else:
        await service.mark_as_read(notification_id=notification.id, user_id=notification.user_id)

        repository.get_by_id.assert_awaited_once_with(id=notification.id)

        repository.mark_status.assert_awaited_once_with(
            notification_id=notification.id,
            status=NotificationStatus.READ
        )

async def test_create_notification(service, repository):
    notification = await service.create_notification(
        user_id=uuid.uuid4(),
        title="test_title",
        channel=NotificationChannel.IN_APP,
        message="test_message",
    )

    assert notification.channel == NotificationChannel.IN_APP
    repository.create.assert_awaited_once()


    
