"""Module that handles the methods to map the SmartSheet response to a
protocol_id."""

import logging
from typing import List, Optional

from pydantic import ValidationError

from aind_metadata_service.client import StatusCodes
from aind_metadata_service.models import ProtocolInformation
from aind_metadata_service.response_handler import ModelResponse
from aind_metadata_service.smartsheet.mapper import SmartSheetMapper
from aind_metadata_service.smartsheet.models import SheetRow
from aind_metadata_service.smartsheet.protocols.models import (
    ProtocolsColumnNames,
)


class ProtocolsMapper(SmartSheetMapper):
    """Primary class to handle mapping data models and returning a response"""

    def _map_row_to_protocol(
        self, row: SheetRow, input_protocol_name: str
    ) -> Optional[ProtocolInformation]:
        """
        Map a row to an optional funding model.
        Parameters
        ----------
        row : SheetRow
        input_protocol_name : str
          The protocol name the user inputs

        Returns
        -------
        Union[ProtocolInformation, None]
          None if the protocol name in the row doesn't match the
          input_protocol_name. Otherwise, will try to return a valid
          ProtocolInformation model. If there is some data entry mistake, then
          it will return a model as good as it can.
        """

        row_dict = self.map_row_to_dict(row)
        protocol_information = {
            "procedure_name": row_dict.get(
                ProtocolsColumnNames.PROCEDURE_NAME
            ),
            "protocol_type": row_dict.get(ProtocolsColumnNames.PROTOCOL_TYPE),
            "protocol_name": row_dict.get(ProtocolsColumnNames.PROTOCOL_NAME),
            "doi": row_dict.get(ProtocolsColumnNames.DOI),
            "version": row_dict.get(ProtocolsColumnNames.VERSION),
            "protocol_collection": row_dict.get(
                ProtocolsColumnNames.PROTOCOL_COLLECTION
            ),
        }

        if input_protocol_name != protocol_information["protocol_name"]:
            return None
        else:
            try:
                return ProtocolInformation.model_validate(protocol_information)
            except ValidationError:
                return ProtocolInformation.model_construct(
                    **protocol_information
                )

    def _get_protocol_list(
        self, protocol_name: str
    ) -> List[ProtocolInformation]:
        """
        Return a list of Protocol Information for a given protocol name
        Parameters
        ----------
        protocol_name : str
          The protocol name that the user inputs.

        Returns
        -------
        List[ProtocolInformation]
          A list of ProtocolInformation models. They might not necessarily pass
          validation checks.
        """
        rows_associated_with_protocol_name: List[ProtocolInformation] = []
        for row in self.model.rows:
            opt_protocol: Optional[ProtocolInformation] = (
                self._map_row_to_protocol(
                    row=row, input_protocol_name=protocol_name
                )
            )
            if opt_protocol is not None:
                rows_associated_with_protocol_name.append(opt_protocol)
        return rows_associated_with_protocol_name

    def _get_model_response(self) -> ModelResponse:
        """
        Return a ModelResponse
        Returns
        -------
        ModelResponse
          Will either be an internal server error response or a database
          responded response. Validation checks are performed downstream.

        """
        try:
            protocol_list = self._get_protocol_list(
                protocol_name=self.input_id
            )
            return ModelResponse(
                aind_models=protocol_list, status_code=StatusCodes.DB_RESPONDED
            )
        except Exception as e:
            logging.error(repr(e))
            return ModelResponse.internal_server_error_response()
