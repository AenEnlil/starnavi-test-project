from .base import BaseAppSettings


class TestAppSettings(BaseAppSettings):
    MONGO_URL: str
    DATABASE_NAME: str = 'test_database'

    USE_AI_FOR_TEXT_VALIDATION: bool = False
