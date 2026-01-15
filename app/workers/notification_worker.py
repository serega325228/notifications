import asyncio
import structlog

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository
from app.services.notification_service import NotificationService
from app.db.db import async_session_maker
from app.services.user_service import UserService

log = structlog.get_logger(__name__)

async def run_worker():
    log.info("worker_pool_started", workers=5)

    workers = [
        asyncio.create_task(process_loop(i))
        for i in range(5)
    ]
    await asyncio.gather(*workers)

async def process_loop(worker_id: int):
    log.info("worker started", worker_id=worker_id)
    async with async_session_maker() as session:
        repo = NotificationRepository(session=session)
        user_service = UserService(
            user_repo=UserRepository(session=session)
        )
        service = NotificationService(
            notification_repo=repo,
            user_service=user_service
        )

        while True: 
            await process_one(session, service, worker_id)

async def process_one(
        session: AsyncSession,
        service: NotificationService,
        worker_id: int
    ):
    async with session.begin():
        notifications = await service.get_processing(limit=10)

    if not notifications:
        log.debug(
            "worker_idle",
            worker_id=worker_id
        )
        await asyncio.sleep(1)
        return
    
    log.info(
        "worker_batch_received",
        worker_id=worker_id,
        batch_size=len(notifications)
    )
    
    for n in notifications:
        log.info(
            "worker_notification_processing_started",
            worker_id=worker_id,
            notification_id=n.id
        )

        try:
            async with session.begin():
                await service.process_sending(notification=n)
                log.info(
                "worker_notification_processed",
                worker_id=worker_id,
                notification_id=n.id
            )
                
        except Exception:
            log.exception(
                "worker_notification_processing_failed",
                worker_id=worker_id,
                notification_id=n.id
            )

def main():
    asyncio.run(run_worker())

if __name__ == "__main__":
    main()