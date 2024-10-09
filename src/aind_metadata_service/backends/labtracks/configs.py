"""Module for settings to connect to LabTracks backend"""

from urllib.parse import quote_plus

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings needed to connect to LabTracks Database"""

    # noinspection SpellCheckingInspection
    model_config = SettingsConfigDict(env_prefix="LABTRACKS_")
    # noinspection SpellCheckingInspection
    driver: str = Field(
        default="FreeTDS&tds_version=8.0",
        title="Driver",
        description="ODBC Driver used to connect to LabTracks.",
        validation_alias=AliasChoices(
            "odbc_driver",
            "ODBC_DRIVER",
            "LABTRACKS_ODBC_DRIVER",
        ),
    )
    host: str = Field(
        ...,
        title="Server",
        description="Host address of the LabTracks Server.",
    )
    port: int = Field(
        ..., title="Port", description="Port number of the LabTracks Server"
    )
    database: str = Field(
        ..., title="Database", description="Name of the database."
    )
    user: str = Field(..., title="User", description="Username.")
    password: SecretStr = Field(..., title="Password", description="Password.")

    @property
    def db_connection_str(self):
        """Compute the connection string from other settings"""
        encoded_password = quote_plus(self.password.get_secret_value())
        return (
            f"mssql+pyodbc://{self.user}:{encoded_password}@"
            f"{self.host}:{self.port}/{self.database}?driver={self.driver}"
        )
