from contextlib import asynccontextmanager
import sys
import structlog
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.api.middlewares.user import user_middleware
from app.api.routers.ui import router as ui
from app.db.db import engine
from app.logger.logging_config import setup_logging
from app.logger.structlog_config import setup_structlog
from app.api.routers.health import router as health
from app.api.routers.events import router as events
from app.api.routers.notifications import router as notifications

setup_logging()
setup_structlog()

log = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        log.info("FastAPI startup")
        yield
        log.info("FastAPI shutdown")

app = FastAPI(lifespan=lifespan)

app.middleware("http")(user_middleware)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

app.include_router(health)
app.include_router(events)
app.include_router(notifications)
app.include_router(ui)

