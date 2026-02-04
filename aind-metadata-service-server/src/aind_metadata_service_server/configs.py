"""Module for settings to connect to backend"""

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    ### Settings needed to connect to a database or website.
    We will just connect to an example website.
    """

    model_config = SettingsConfigDict(env_prefix="AIND_METADATA_SERVICE_")

    labtracks_host: HttpUrl = Field(
        ..., description="Host address for labtracks endpoint"
    )
    mgi_host: HttpUrl = Field(..., description="Host address for mgi endpoint")
    slims_host: HttpUrl = Field(
        ..., description="Host address for slims endpoint"
    )
    sharepoint_host: HttpUrl = Field(
        ..., description="Host address for sharepoint endpoint"
    )
    tars_host: HttpUrl = Field(
        ..., description="Host address for tars endpoint"
    )
    smartsheet_host: HttpUrl = Field(
        ..., description="Host address for smartsheet endpoint"
    )
    session_json_host: HttpUrl = Field(
        ..., description="Host address for metadata mapper service"
    )
    aind_data_schema_v1_host: HttpUrl = Field(
        ..., description="Host address for v1 service"
    )
    docdb_api_host: str = Field(
        ..., description="Host address for data access api"
    )
    dataverse_host: HttpUrl = Field(
        ..., description="Host address for dataverse endpoint"
    )


def get_settings():
    """Return Settings object"""
    return Settings()
