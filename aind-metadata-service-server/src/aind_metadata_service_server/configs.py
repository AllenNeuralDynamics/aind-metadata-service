"""Module for settings to connect to backend"""
from dataclasses import Field

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    ### Settings needed to connect to a database or website.
    We will just connect to an example website.
    """

    model_config = SettingsConfigDict(env_prefix="AIND_METADATA_SERVICE_")

    labtracks_host: HttpUrl = Field(
        ...,
        description="Host address for labtracks endpoint"
    )


def get_settings():
    return Settings()
