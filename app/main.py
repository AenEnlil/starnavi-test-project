from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from pytz import utc

from app.api import api_router
from app.logger import get_logger
from app.config import get_settings


def get_application() -> FastAPI:
    settings = get_settings()

    if settings.LOGS_ENABLED:
        logger = get_logger()

    application = FastAPI()

    application.include_router(api_router, prefix='/api/v1')
    return application


jobstores = {
    'default': MemoryJobStore()
}

executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

scheduler = AsyncIOScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)

app = get_application()


@app.on_event('startup')
async def startup_event():
    scheduler.start()


@app.on_event('shutdown')
async def shutdown_event():
    scheduler.shutdown()
