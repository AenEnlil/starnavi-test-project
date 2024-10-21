import pytest

from typing import Generator, Any

from fastapi import FastAPI

from app.main import get_application
from app.config import get_settings
from app.database import mongo_client

settings = get_settings()


@pytest.fixture()
async def app() -> Generator[FastAPI, Any, None]:
    _app = get_application()
    yield _app

    mongo_client.drop_database(get_settings().DATABASE_NAME)
    mongo_client.close()
