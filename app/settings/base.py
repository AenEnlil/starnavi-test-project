from enum import Enum
from os import getenv

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvTypes(Enum):
    local: str = 'local'
    test: str = 'test'


class BaseAppSettings(BaseSettings):
    environment: AppEnvTypes = AppEnvTypes.local

    SECRET_KEY: str
    ACCESS_TOKEN_LIFETIME_MINUTES: int = 15
    ALGORITHM: str

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
