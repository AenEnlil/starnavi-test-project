from fastapi import FastAPI

from app.config import get_settings


def get_application() -> FastAPI:
    settings = get_settings()

    application = FastAPI()
    return application


app = get_application()

