"""Module for slims client"""

import logging

from pydantic import Extra, Field, SecretStr
from pydantic_settings import BaseSettings
from slims.criteria import equals
from slims.internal import Record
from slims.slims import Slims

from aind_metadata_service.slims.models import ContentsTableRow


class SlimsSettings(BaseSettings):
    """Configuration class. Mostly a wrapper around smartsheet.Smartsheet
    class constructor arguments."""

    username: str = Field(..., description="User name")
    password: SecretStr = Field(..., description="Password")
    host: str = Field(..., description="host")
    db: str = Field(default="slims", description="Database")

    class Config:
        """Set env prefix and forbid extra fields."""

        env_prefix = "SLIMS_"
        extra = Extra.forbid


class SlimsClient:
    """Client to connect to slims db"""

    def __init__(self, settings: SlimsSettings):
        """Class constructor for slims client"""
        self.settings = settings
        self.client = Slims(
            settings.db,
            settings.host,
            settings.username,
            settings.password.get_secret_value(),
        )

    def get_record(self, subject_id: str) -> Record:
        """
        Retrieve a record from the Contents Table
        Parameters
        ----------
        subject_id : str
          Labtracks id of subject to retrieve record for

        Returns
        -------
        Record
          A single slims Record

        """
        try:
            content_record = self.client.fetch(
                "Content",
                equals(
                    ContentsTableRow.model_fields["cntn_cf_labtracksId"].title,
                    subject_id,
                ),
                start=0,
                end=1,
            )[0]
            return content_record
        except Exception as e:
            logging.error(repr(e))
            raise Exception(e)
