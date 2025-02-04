"""Module for settings to connect to SLIMS server"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings needed to connect to SLIMS Database"""

    # noinspection SpellCheckingInspection
    model_config = SettingsConfigDict(env_prefix="SLIMS_")
    url: str = Field(
        ...,
        title="SLIMS URL",
        description="URL of SLIMS REST Endpoint.",
    )
    username: str = Field(..., title="User Name", description="User name.")
    password: SecretStr = Field(..., title="Password", description="Password.")


def get_settings() -> Settings:
    """Utility method to return a settings object."""
    return Settings()
