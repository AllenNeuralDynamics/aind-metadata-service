"""Module that handles the methods to map the SmartSheet response to a
protocol_id."""

import json
import logging
from typing import List, Optional, Dict
from pydantic import ValidationError

from aind_metadata_service.client import StatusCodes
from aind_metadata_service.models import ProtocolInformation
from aind_metadata_service.response_handler import ModelResponse
from aind_metadata_service.smartsheet.mapper import SmartSheetMapper
from aind_metadata_service.smartsheet.models import SheetRow
from aind_metadata_service.smartsheet.protocols.models import (
    ProtocolsColumnNames,
    ProtocolNames
)
from aind_data_schema.core.procedures import (
    NanojectInjection,
    IontophoresisInjection,
    Perfusion,
    Craniotomy,
    ProtectiveMaterial,
    Surgery
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

    @staticmethod
    def get_protocols_mapping(response: ModelResponse) -> Dict:
        """Creates a dictionary mapping procedure models to protocols"""
        surgery_dict = {}
        if len(response.aind_models) > 0:
            procedures = response.aind_models[0]
            if isinstance(procedures, Surgery):
                surgery_dict[procedures] = ProtocolNames.SURGERY
            for subject_procedure in procedures.subject_procedures:
                # TODO: handle Surgery one maybe another way
                for procedure in subject_procedure.procedures:
                    if isinstance(procedure, NanojectInjection):
                        surgery_dict[procedure] = ProtocolNames.INJECTION_NANOJECT
                    elif isinstance(procedure, IontophoresisInjection):
                        surgery_dict[procedure] = ProtocolNames.INJECTION_IONTOPHORESIS
                    elif isinstance(procedure, Perfusion):
                        surgery_dict[procedure] = ProtocolNames.PERFUSION
                    elif isinstance(procedure, Craniotomy):
                        if procedure.protective_material == ProtectiveMaterial.DURAGEL:
                            surgery_dict[procedure] = ProtocolNames.DURAGEL_APPLICATION
        return surgery_dict

    @staticmethod
    def integrate_protocols(response: ModelResponse, protocols_mapping: Dict) -> ModelResponse:
        """Merges protocols_response with procedures_response"""
        output_aind_models = []
        status_code = response.status_code
        if len(response.aind_models) > 0:
            pre_procedures = response.aind_models[0]
            if isinstance(pre_procedures, Surgery):
                pre_procedures.protocol_id = protocols_mapping[pre_procedures]
            for subject_procedure in pre_procedures.subject_procedures:
                for procedure in subject_procedure.procedures:
                    smartsheet_response = protocols_mapping.get(subject_procedure)
                    if (
                            smartsheet_response.status_code == StatusCodes.DB_RESPONDED.value
                            or smartsheet_response.status_code == StatusCodes.VALID_DATA.value
                            or smartsheet_response.status_code == StatusCodes.INVALID_DATA.value
                    ):
                        data = json.loads(smartsheet_response.body)["data"]
                        procedure.protocol_id = data["doi"]
                    elif (
                            smartsheet_response.status_code == StatusCodes.NO_DATA_FOUND.value
                    ):
                        pass
                    else:
                        status_code = StatusCodes.MULTI_STATUS
                output_aind_models = [pre_procedures]
        return ModelResponse(
            aind_models=output_aind_models, status_code=status_code
        )
