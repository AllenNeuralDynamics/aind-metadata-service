"""Module to instantiate a client to connect to Smartsheet and provide helpful
methods to retrieve data."""

import logging
from typing import Optional

from pydantic import Extra, Field, SecretStr
from pydantic_settings import BaseSettings
from smartsheet import Smartsheet
from starlette.responses import JSONResponse

from aind_metadata_service import __version__
from aind_metadata_service.client import StatusCodes


class SmartsheetSettings(BaseSettings):
    """Configuration class. Mostly a wrapper around smartsheet.Smartsheet
    class constructor arguments."""

    access_token: SecretStr = Field(
        ..., description="API token can be created in Smartsheet UI"
    )
    sheet_id: int = Field(
        ...,
        description=(
            "Sheet ID to query. Can be found in Smartsheet under "
            "File | Properties."
        ),
    )
    user_agent: Optional[str] = Field(
        default=f"AIND_Metadata_Service/{__version__}",
        description=(
            "The user agent to use when making requests. "
            "Helps identify requests coming from this app."
        ),
    )
    max_connections: int = Field(
        default=8, description="Maximum connection pool size."
    )

    class Config:
        """Set env prefix and forbid extra fields."""

        env_prefix = "SMARTSHEET_"
        extra = Extra.forbid


class SmartSheetClient:
    """Main client to connect to a Smartsheet sheet. Requires an API token
    and the sheet id."""

    def __init__(self, smartsheet_settings: SmartsheetSettings):
        """
        Class constructor
        Parameters
        ----------
        smartsheet_settings : SmartsheetSettings
        """
        self.smartsheet_settings = smartsheet_settings
        self.smartsheet_client = Smartsheet(
            user_agent=self.smartsheet_settings.user_agent,
            max_connections=self.smartsheet_settings.max_connections,
            access_token=(
                self.smartsheet_settings.access_token.get_secret_value()
            ),
        )

    def get_sheet(self) -> JSONResponse:
        """Retrieve the sheet defined by the settings sheet_id."""
        try:
            smartsheet_response = self.smartsheet_client.Sheets.get_sheet(
                self.smartsheet_settings.sheet_id
            )
            smartsheet_json = smartsheet_response.to_json()
            return JSONResponse(
                status_code=StatusCodes.DB_RESPONDED.value,
                content=(
                    {"message": "Retrieved data", "data": smartsheet_json}
                ),
            )
        except Exception as e:
            logging.error(f"{e.__class__.__name__}{e.args}")
            return JSONResponse(
                status_code=StatusCodes.INTERNAL_SERVER_ERROR.value,
                content=(
                    {"message": "Error connecting to server", "data": None}
                ),
            )
