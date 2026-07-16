"""FastAPI dependency injection utilities."""

from typing import Annotated
from fastapi import Depends

from .config import Settings, settings


def get_settings() -> Settings:
    """Dependency to get application settings."""
    return settings


SettingsDep = Annotated[Settings, Depends(get_settings)]
