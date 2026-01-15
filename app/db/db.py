from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from .settings import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10
)

async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)