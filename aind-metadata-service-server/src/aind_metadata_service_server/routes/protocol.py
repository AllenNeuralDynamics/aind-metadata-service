"""Module to handle protocol endpoints"""

from fastapi import APIRouter, Depends, Path

from aind_metadata_service_server.mappers.protocol import ProtocolMapper
from aind_metadata_service_server.response_handler import (
    ModelResponse,
    StatusCodes,
)
from aind_metadata_service_server.sessions import get_smartsheet_api_instance

router = APIRouter()


@router.get("/protocols/{protocol_name}")
async def get_protocols(
    protocol_name: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample protocol name",
                "description": "Example protocol name",
                "value": (
                    "Tetrahydrofuran and Dichloromethane Delipidation of a "
                    "Whole Mouse Brain"
                ),
            }
        },
    ),
    smartsheet_api_instance=Depends(get_smartsheet_api_instance),
):
    """
    ## Protocols
    Return Protocols metadata.
    """
    protocols_response = await smartsheet_api_instance.get_protocols(
        protocol_name=protocol_name, _request_timeout=10
    )
    mappers = [
        ProtocolMapper(smartsheet_protocol=smartsheet_protocol)
        for smartsheet_protocol in protocols_response
    ]
    protocols = [mapper.map_to_protocol_information() for mapper in mappers]
    response_handler = ModelResponse(
        aind_models=protocols, status_code=StatusCodes.DB_RESPONDED
    )
    response = response_handler.map_to_json_response()
    return response
