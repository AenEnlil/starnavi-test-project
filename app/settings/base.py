from enum import Enum
from os import getenv

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvTypes(Enum):
    local: str = 'local'
    test: str = 'test'


class BaseAppSettings(BaseSettings):
    environment: AppEnvTypes = AppEnvTypes.local

    AI_MODEL_NAME: str = "gemini-1.5-flash-002"
    GOOGLE_CLOUD_PROJECT_LOCATION: str = "us-central1"
    GOOGLE_CLOUD_PROJECT_ID: str
    GOOGLE_CLOUD_PROJECT_CREDENTIALS_PATH: str = '/app/vertex_ai_core/service_account_credentials.json'

    SECRET_KEY: str
    ACCESS_TOKEN_LIFETIME_MINUTES: int = 15
    ALGORITHM: str

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
