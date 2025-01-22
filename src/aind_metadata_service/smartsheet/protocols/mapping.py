"""Module that handles the methods to map the SmartSheet response to a
protocol_id."""

import json
import logging
from typing import Dict, List, Optional

from aind_data_schema.core.procedures import (
    Craniotomy,
    IontophoresisInjection,
    NanojectInjection,
    Perfusion,
    ProtectiveMaterial,
    Surgery,
)
from pydantic import ValidationError

from aind_metadata_service.client import StatusCodes
from aind_metadata_service.models import ProtocolInformation
from aind_metadata_service.response_handler import ModelResponse
from aind_metadata_service.smartsheet.mapper import SmartSheetMapper
from aind_metadata_service.smartsheet.models import SheetRow
from aind_metadata_service.smartsheet.protocols.models import (
    ProtocolNames,
    ProtocolsColumnNames,
)


class ProtocolsMapper(SmartSheetMapper):
    """Primary class to handle mapping data models and returning a response"""

    def _map_row_to_protocol(
        self, row: SheetRow, input_protocol_name: Optional[str]
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


class ProtocolsIntegrator:
    """Methods to integrate Protocols into Procedures"""

    @staticmethod
    def _get_protocol_name(procedure):
        """Gets protocol name based on procedure type"""
        if isinstance(procedure, NanojectInjection):
            return ProtocolNames.INJECTION_NANOJECT.value
        elif isinstance(procedure, IontophoresisInjection):
            return ProtocolNames.INJECTION_IONTOPHORESIS.value
        elif isinstance(procedure, Perfusion):
            return ProtocolNames.PERFUSION.value
        elif isinstance(procedure, Craniotomy):
            if procedure.protective_material == ProtectiveMaterial.DURAGEL:
                return ProtocolNames.DURAGEL_APPLICATION.value
        else:
            return None

    def get_protocols_list(self, response: ModelResponse) -> List:
        """Creates a list of protocol names from procedures list"""
        protocol_list = []
        if len(response.aind_models) > 0:
            procedures = response.aind_models[0]
            for subject_procedure in procedures.subject_procedures:
                if isinstance(subject_procedure, Surgery):
                    protocol_list.append(ProtocolNames.SURGERY.value)
                if not hasattr(subject_procedure, "procedures"):
                    continue
                for procedure in subject_procedure.procedures:
                    protocol_name = self._get_protocol_name(
                        procedure=procedure
                    )
                    protocol_list.append(protocol_name)
        return protocol_list

    def integrate_protocols(
        self, response: ModelResponse, protocols_mapping: Dict
    ) -> ModelResponse:
        """
        Merges protocols responses with procedures response
        Parameters
        ----------
        response: ModelResponse
             Merged response from procedures endpoints
        protocols_mapping: dict
             Dictionary mapping protocol names to info from smartsheet
        Returns
        -------
        Procedures response with protocols
        """
        output_aind_models = []
        status_code = response.status_code
        if len(response.aind_models) > 0:
            pre_procedures = response.aind_models[0]
            for subject_procedure in pre_procedures.subject_procedures:
                if (
                    isinstance(subject_procedure, Surgery)
                    and hasattr(subject_procedure, "experimenter_full_name")
                    and "NSB" in subject_procedure.experimenter_full_name
                ):
                    protocol_name = ProtocolNames.SURGERY.value
                    smartsheet_response = protocols_mapping.get(protocol_name)
                    if (
                        smartsheet_response.status_code
                        == StatusCodes.DB_RESPONDED.value
                        or smartsheet_response.status_code
                        == StatusCodes.VALID_DATA.value
                        or smartsheet_response.status_code
                        == StatusCodes.INVALID_DATA.value
                    ):
                        data = json.loads(smartsheet_response.body)["data"]
                        subject_procedure.protocol_id = data["doi"]
                    elif (
                        smartsheet_response.status_code
                        == StatusCodes.NO_DATA_FOUND.value
                    ):
                        pass
                    else:
                        status_code = StatusCodes.MULTI_STATUS
                if not hasattr(subject_procedure, "procedures"):
                    output_aind_models = [pre_procedures]
                    continue
                for procedure in subject_procedure.procedures:
                    protocol_name = self._get_protocol_name(procedure)
                    smartsheet_response = protocols_mapping.get(protocol_name)
                    if (
                        smartsheet_response.status_code
                        == StatusCodes.DB_RESPONDED.value
                        or smartsheet_response.status_code
                        == StatusCodes.VALID_DATA.value
                        or smartsheet_response.status_code
                        == StatusCodes.INVALID_DATA.value
                    ):
                        data = json.loads(smartsheet_response.body)["data"]
                        procedure.protocol_id = data["doi"]
                    elif (
                        smartsheet_response.status_code
                        == StatusCodes.NO_DATA_FOUND.value
                    ):
                        pass
                    else:
                        status_code = StatusCodes.MULTI_STATUS
                output_aind_models = [pre_procedures]
        return ModelResponse(
            aind_models=output_aind_models, status_code=status_code
        )
