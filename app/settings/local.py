from .base import BaseAppSettings


class LocalAppSettings(BaseAppSettings):
    MONGO_URL: str
    DATABASE_NAME: str

    USE_AI_FOR_TEXT_VALIDATION: bool = True
