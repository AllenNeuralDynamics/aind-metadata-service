"""Module for defining redis backend"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings needed to connect to Redis"""

    model_config = SettingsConfigDict(env_prefix="REDIS_")
    host: str = Field(default="redis")
    port: int = Field(default=6379)

    @property
    def connection_str(self):
        """Connection String"""
        return f"redis://{self.host}:{self.port}"
