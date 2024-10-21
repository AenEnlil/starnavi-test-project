from enum import Enum
from os import getenv

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvTypes(Enum):
    local: str = 'local'
    test: str = 'test'


class BaseAppSettings(BaseSettings):
    environment: AppEnvTypes = AppEnvTypes.local

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
