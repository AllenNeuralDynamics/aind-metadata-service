"""Module that handles the methods to map the ProtocolsModel response to the
Protocols model."""

import logging
from typing import Optional

from pydantic import ValidationError

from aind_smartsheet_service_async_client.models import ProtocolsModel
from aind_metadata_service_server.models import ProtocolInformation


class ProtocolMapper:
    """Primary class to handle mapping ProtocolsModel to ProtocolInformation models"""

    def __init__(self, smartsheet_protocol: ProtocolsModel):
        """
        Initialize mapper with a single ProtocolsModel instance

        Parameters
        ----------
        smartsheet_protocol : ProtocolsModel
            Single protocol model from the service
        """
        self.smartsheet_protocol = smartsheet_protocol

    def map_to_protocol_information(self) -> Optional[ProtocolInformation]:
        """
        Map ProtocolsModel to ProtocolInformation. Will attempt to return
        a valid model. If there are any validation errors, then an invalid
        model will be returned.

        Returns
        -------
        Optional[ProtocolInformation]
            ProtocolInformation model or None if all fields are empty
        """
        smartsheet_protocol = self.smartsheet_protocol
        procedure_name = smartsheet_protocol.procedure_name
        protocol_type = smartsheet_protocol.protocol_type
        protocol_name = smartsheet_protocol.protocol_name
        doi = smartsheet_protocol.doi
        version = smartsheet_protocol.version
        protocol_collection = smartsheet_protocol.protocol_collection

        if (
            procedure_name is None
            and protocol_type is None
            and protocol_name is None
            and doi is None
            and version is None
            and protocol_collection is None
        ):
            return None

        try:
            return ProtocolInformation(
                procedure_name=procedure_name,
                protocol_type=protocol_type,
                protocol_name=protocol_name,
                doi=doi,
                version=version,
                protocol_collection=protocol_collection,
            )
        except ValidationError as e:
            logging.warning(f"Validation error creating ProtocolInformation model: {e}")
            return ProtocolInformation.model_construct(
                procedure_name=procedure_name,
                protocol_type=protocol_type,
                protocol_name=protocol_name,
                doi=doi,
                version=version,
                protocol_collection=protocol_collection,
            )


