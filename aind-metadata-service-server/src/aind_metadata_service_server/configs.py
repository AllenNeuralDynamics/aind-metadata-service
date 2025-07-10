"""Module for settings to connect to backend"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    ### Settings needed to connect to a database or website.
    We will just connect to an example website.
    """

    model_config = SettingsConfigDict(env_prefix="AIND_METADATA_SERVICE_")
