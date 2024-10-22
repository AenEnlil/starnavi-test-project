from fastapi import FastAPI

from app.api import api_router
from app.config import get_settings


def get_application() -> FastAPI:
    settings = get_settings()

    application = FastAPI()

    application.include_router(api_router, prefix='/api/v1')
    return application


app = get_application()

