"""Module that handles the methods to map the SmartSheet response to the
aind-data-schema Funding model."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from aind_metadata_service.response_handler import ModelResponse
from aind_metadata_service.smartsheet.client import SmartSheetClient
from aind_metadata_service.smartsheet.models import SheetFields


class SmartSheetMapper(ABC):
    """Primary class to handle mapping data models and returning a response"""

    def __init__(self, smart_sheet_client: SmartSheetClient):
        """
        Class Constructor
        Parameters
        ----------
        smart_sheet_client: SmartSheetClient
        """
        self.smart_sheet_client = smart_sheet_client

    @property
    def sheet_contents(self):
        """Return sheet contents as a json string."""
        return self.smart_sheet_client.get_sheet()

    @property
    def _column_id_map(self) -> Dict[str, Any]:
        """SmartSheet uses integer ids for the columns. We need a way to
        map the column titles to the ids so we can retrieve information using
        just the titles."""
        return {c.title: c.id for c in self.model.columns}

    @property
    def model(self) -> SheetFields:
        """Convert sheet contents to a pydantic model"""
        return SheetFields.model_validate_json(self.sheet_contents)

    @abstractmethod
    def get_model_response(self, input_id: str) -> ModelResponse:
        """
        Return a ModelResponse for a given id.
        Parameters
        ----------
        input_id : str
          The id with which to extract information

        Returns
        -------
        ModelResponse
          Will either be an internal server error response or a database
          responded response. Validation checks are performed downstream.

        """
