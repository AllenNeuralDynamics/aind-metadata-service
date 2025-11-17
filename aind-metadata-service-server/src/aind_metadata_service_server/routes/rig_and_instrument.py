"""Module to handle rig and instrument endpoints"""

import hashlib
from asyncio import gather, to_thread
from uuid import UUID

from aind_data_access_api.document_db import Client as DocDBClient
from aind_slims_service_async_client import DefaultApi
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from requests import HTTPError

from aind_metadata_service_server.sessions import (
    get_instruments_client,
    get_slims_api_instance,
)

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
    docdb_client: DocDBClient = Depends(get_instruments_client),
):
    """
    ## Instrument
    Return an Instrument.
    """

    if partial_match:
        filter_query = {"instrument_id": {"$regex": instrument_id}}
    else:
        filter_query = {"instrument_id": instrument_id}
    slims_instruments, docdb_instruments = await gather(
        slims_api_instance.get_aind_instrument(
            input_id=instrument_id, partial_match=partial_match
        ),
        to_thread(
            docdb_client.retrieve_docdb_records,
            filter_query=filter_query,
            projection={"_id": 0},
        ),
    )
    instruments = []
    seen_ids = set()
    for instrument in docdb_instruments:
        seen_ids = instrument["instrument_id"]
        instruments.append(instrument)
    for instrument in slims_instruments:
        if instrument.get("instrument_id") not in seen_ids:
            instruments.append(instrument)
    if len(instruments) == 0:
        raise HTTPException(status_code=404, detail="Not found")
    else:
        return JSONResponse(
            status_code=400,
            content=instruments,
            headers={"X-Error-Message": "Models have not been validated."},
        )


@router.post("/api/v2/instrument")
def post_instrument(
    data: dict = Body(...),
    docdb_client: DocDBClient = Depends(get_instruments_client),
):
    """
    ## Instrument
    Save an instrument to a database.
    """
    if (
        data.get("instrument_id") is None
        or not isinstance(data["instrument_id"], str)
        or data["instrument_id"].strip() == ""
    ):
        return JSONResponse(
            status_code=406, content={"message": "Missing instrument_id."}
        )
    elif (
        data.get("modification_date") is None
        or not isinstance(data["modification_date"], str)
        or data["modification_date"].strip() == ""
    ):
        return JSONResponse(
            status_code=406, content={"message": "Missing modification_date."}
        )
    else:
        instrument_id = data["instrument_id"]
        modification_date = data["modification_date"]
        concat_fields = instrument_id + modification_date
        encoded_string = concat_fields.encode("utf-8")
        md5_hash = hashlib.md5(encoded_string).hexdigest()
        data["_id"] = str(UUID(md5_hash))
        try:
            response = docdb_client.insert_one_docdb_record(data)
            return response.json()
        except HTTPError as e:
            if "duplicate key error" in e.response.text:
                return JSONResponse(
                    status_code=400,
                    content=(
                        {
                            "message": (
                                "Record for instrument_id and "
                                "modification_date already exists!"
                            )
                        }
                    ),
                )
            else:
                return JSONResponse(
                    status_code=500,
                    content={"message": "Internal Server Error"},
                )
