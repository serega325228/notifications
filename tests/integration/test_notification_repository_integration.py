from app.db.models.enums import NotificationStatus
from datetime import datetime, timezone, timedelta

async def test_get_pending(repository, session, notification_factory, user_service):
    
    user = await user_service.create_user()

    for _ in range(3):
        await repository.create(
            notification=notification_factory(user_id=user.id, status=NotificationStatus.PENDING)
        )

    for _ in range(2):
        await repository.create(
            notification=notification_factory(user_id=user.id, status=NotificationStatus.SENT)
        )

    await repository.create(
        notification=notification_factory(user_id=user.id, status=NotificationStatus.FAILED)
    )

    await session.commit()

    result = await repository.get_pending(limit=10)

    assert len(result) == 3
    assert all(n.status == NotificationStatus.PENDING for n in result)

    
async def test_update_attempts(repository, notification_factory, user_service):

    user = await user_service.create_user()

    notification = notification_factory(user_id=user.id)

    await repository.create(notification=notification)

    next_attempt_at = datetime.now(timezone.utc) + timedelta(seconds=3)

    result = await repository.update_attempts(
        notification_id=notification.id, 
        new_attempts=1, 
        next_attempt_at=next_attempt_at
    )

    assert result.attempts == 1
    assert result.next_attempt_at == next_attempt_at

async def test_mark_status(repository, notification_factory, user_service):

    user = await user_service.create_user()

    notification = notification_factory(user_id=user.id)

    await repository.create(notification=notification)

    result = await repository.mark_status(
        notification_id=notification.id,
        status=NotificationStatus.READ
    )

    assert result.status == NotificationStatus.READ
