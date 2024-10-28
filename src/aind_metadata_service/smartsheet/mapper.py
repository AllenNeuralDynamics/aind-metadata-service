"""Module that handles the methods to map the SmartSheet response to the
aind-data-schema Funding model."""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from starlette.responses import JSONResponse

from aind_metadata_service.client import StatusCodes
from aind_metadata_service.response_handler import ModelResponse
from aind_metadata_service.smartsheet.models import SheetFields, SheetRow


class SmartSheetMapper(ABC):
    """Primary class to handle mapping data models and returning a response"""

    def __init__(self, smart_sheet_response: JSONResponse, input_id: str):
        """
        Class Constructor
        Parameters
        ----------
        smart_sheet_response : JSONResponse
          JSON Response when querying smart sheet
        input_id : str
          Key to filter results
        """
        self.smart_sheet_response = smart_sheet_response
        self.input_id = input_id

    @property
    def sheet_contents(self) -> Optional[str]:
        """Parse data out of JSONResponse object"""
        json_content = json.loads(self.smart_sheet_response.body)
        return json_content["data"]

    @property
    def _column_id_map(self) -> Dict[int, str]:
        """SmartSheet uses integer ids for the columns. We need a way to
        map the column titles to the ids so we can retrieve information using
        just the titles."""
        return {c.id: c.title for c in self.model.columns}

    @property
    def model(self) -> SheetFields:
        """Convert sheet contents to a pydantic model"""
        return SheetFields.model_validate_json(self.sheet_contents)

    def map_row_to_dict(self, row: SheetRow) -> Dict[str, Any]:
        """
        Maps a row into a dictionary that maps the column names to their values
        Parameters
        ----------
        row : SheetRow
          A SheetRow that will be parsed. This a list of cells with a columnId
          and a cell value.

        Returns
        -------
        Dict[str, Any]
          The list of row cells is converted to a dictionary.

        """
        output_dict = {}
        for cell in row.cells:
            column_id = cell.columnId
            column_name = self._column_id_map[column_id]
            output_dict[column_name] = cell.value
        return output_dict

    @abstractmethod
    def _get_model_response(self) -> ModelResponse:
        """Parse the sheet contents into a ModelResponse"""

    def get_model_response(self) -> ModelResponse:
        """
        Return a ModelResponse given the smart response.

        Returns
        -------
        ModelResponse
          Will either be an internal server error response or a database
          responded response. Validation checks are performed downstream.

        """
        if (
            self.smart_sheet_response.status_code
            == StatusCodes.INTERNAL_SERVER_ERROR.value
        ):
            return ModelResponse.internal_server_error_response()
        elif self.sheet_contents is None:
            return ModelResponse.no_data_found_error_response()
        else:
            return self._get_model_response()
