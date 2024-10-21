from functools import lru_cache
from typing import Dict, Type

from app.settings.base import BaseAppSettings, AppEnvTypes
from app.settings.local import LocalAppSettings
from app.settings.test import TestAppSettings


environments: Dict[AppEnvTypes, Type[BaseAppSettings]] = {
    AppEnvTypes.local: LocalAppSettings,
    AppEnvTypes.test: TestAppSettings
}


@lru_cache
def get_settings():
    environment = BaseAppSettings().environment
    settings = environments[environment]
    return settings()


