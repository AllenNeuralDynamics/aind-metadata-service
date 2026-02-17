"""Module to handle protocol endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Path

from aind_metadata_service_server.mappers.protocol import ProtocolMapper
from aind_metadata_service_server.mappers.responses import map_to_response
from aind_metadata_service_server.sessions import get_smartsheet_api_instance

router = APIRouter()


@router.get(
    "/api/v2/protocols/{protocol_name}",
    responses={
        400: {
            "description": "Validation error in response model.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Validation error in response model."
                    }
                }
            },
        },
        404: {"description": "Not found"},
        500: {"description": "Too many responses"},
    },
)
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
    protocols = [
        mapper.map_to_protocol_information()
        for mapper in mappers
        if mapper.map_to_protocol_information() is not None
    ]
    if len(protocols) == 0:
        raise HTTPException(status_code=404, detail="Not found")
    elif len(protocols) > 1:
        raise HTTPException(
            status_code=500,
            detail=f"Too many responses for {protocol_name}!",
        )
    else:
        return map_to_response(protocols[0])
