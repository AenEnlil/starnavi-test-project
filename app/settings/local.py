from .base import BaseAppSettings


class LocalAppSettings(BaseAppSettings):
    MONGO_URL: str
    DATABASE_NAME: str

