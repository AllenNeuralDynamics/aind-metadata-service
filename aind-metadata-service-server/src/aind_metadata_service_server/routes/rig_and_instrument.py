"""Module to handle rig and instrument endpoints"""

from aind_slims_service_async_client import DefaultApi
from fastapi import APIRouter, Depends, Path, Query

from aind_metadata_service_server.mappers.rig_and_instrument import (
    RigAndInstrumentMapper,
)
from aind_metadata_service_server.response_handler import (
    ModelResponse,
    StatusCodes,
)
from aind_metadata_service_server.sessions import get_slims_api_instance

router = APIRouter()


@router.get("/rig/{rig_id}")
async def get_rig(
    rig_id: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample rig ID",
                "description": "Example rig ID for SLIMS",
                "value": "323_EPHYS1_20250205",
            }
        },
    ),
    partial_match: bool = Query(False, alias="partial_match"),
    slims_api_instance: DefaultApi = Depends(get_slims_api_instance),
):
    """
    ## Rig
    Return a Rig.
    """

    slims_models = await slims_api_instance.get_aind_instrument(
        input_id=rig_id, partial_match=partial_match
    )
    mapper = RigAndInstrumentMapper(slims_models=slims_models)
    rigs = mapper.map_to_rigs()
    response_handler = ModelResponse(
        aind_models=rigs, status_code=StatusCodes.DB_RESPONDED
    )
    response = response_handler.map_to_json_response(validate=False)
    return response


@router.get("/instrument/{instrument_id}")
async def get_instrument(
    instrument_id: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample instrument ID",
                "description": "Example instrument ID for SLIMS",
                "value": "440_SmartSPIM1_20240327",
            }
        },
    ),
    partial_match: bool = Query(False, alias="partial_match"),
    slims_api_instance: DefaultApi = Depends(get_slims_api_instance),
):
    """
    ## Instrument
    Return an Instrument.
    """

    slims_models = await slims_api_instance.get_aind_instrument(
        input_id=instrument_id, partial_match=partial_match
    )
    mapper = RigAndInstrumentMapper(slims_models=slims_models)
    instruments = mapper.map_to_instruments()
    response_handler = ModelResponse(
        aind_models=instruments, status_code=StatusCodes.DB_RESPONDED
    )
    response = response_handler.map_to_json_response(validate=False)
    return response
