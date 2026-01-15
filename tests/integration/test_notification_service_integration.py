from app.db.models.enums import NotificationStatus

async def test_process_sending(user_service, service, repository, notification_factory):
    user = await user_service.create_user()

    notification = notification_factory(user_id=user.id)

    await repository.create(notification=notification)

    await service.mark_as_processing(notification_id=notification.id)

    await service.process_sending(notification=notification)

    saved = await repository.get_by_id(id=notification.id)

    assert saved.status == NotificationStatus.SENT
    assert saved.attempts == 1


