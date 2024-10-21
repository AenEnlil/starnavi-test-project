from .base import BaseAppSettings


class TestAppSettings(BaseAppSettings):
    MONGO_URL: str
    DATABASE_NAME: str = 'test_database'
