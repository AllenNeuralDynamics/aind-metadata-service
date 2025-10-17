"""Module to handle rig and instrument endpoints"""

from aind_slims_service_async_client import DefaultApi
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import JSONResponse

from aind_metadata_service_server.sessions import get_slims_api_instance

router = APIRouter()


@router.get("/api/v2/rig/{rig_id}")
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
    rigs = await slims_api_instance.get_aind_instrument(
        input_id=rig_id, partial_match=partial_match
    )
    if len(rigs) == 0:
        raise HTTPException(status_code=404, detail="Not found")
    else:
        return JSONResponse(
            status_code=400,
            content=rigs,
            headers={"X-Error-Message": "Models have not been validated."},
        )


@router.get("/api/v2/instrument/{instrument_id}")
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

    instruments = await slims_api_instance.get_aind_instrument(
        input_id=instrument_id, partial_match=partial_match
    )
    if len(instruments) == 0:
        raise HTTPException(status_code=404, detail="Not found")
    else:
        return JSONResponse(
            status_code=400,
            content=instruments,
            headers={"X-Error-Message": "Models have not been validated."},
        )
