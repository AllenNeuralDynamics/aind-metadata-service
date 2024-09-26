from pydantic import Field, SecretStr, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


class LabTracksSettings(BaseSettings):
    """Settings needed to connect to LabTracks Database"""

    model_config = SettingsConfigDict(env_prefix="LABTRACKS_")

    odbc_driver: str = Field(
        title="Driver",
        description="ODBC Driver used to connect to LabTracks.",
        validation_alias=AliasChoices(
            "odbc_driver", "ODBC_DRIVER", "LABTRACKS_ODBC_DRIVER"
        )
    )
    server: str = Field(
        title="Server", description="Host address of the LabTracks Server."
    )
    port: str = Field(
        title="Port", description="Port number of the LabTracks Server"
    )
    database: str = Field(
        title="Database", description="Name of the database."
    )
    user: str = Field(title="User", description="Username.")
    password: SecretStr = Field(
        title="Password", description="Password."
    )
