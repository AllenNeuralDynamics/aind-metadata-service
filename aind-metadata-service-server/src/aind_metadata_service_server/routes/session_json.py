"""Module to handle session json endpoints"""

from aind_session_json_service_async_client import (
    DefaultApi,
    JobResponse,
    JobSettings,
)
from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from aind_metadata_service_server.sessions import get_session_json_api_instance

router = APIRouter()


@router.post("/bergamo_session")
async def get_bergamo_session(
    job_settings: JobSettings,
    session_json_api_instance: DefaultApi = Depends(
        get_session_json_api_instance
    ),
):
    """
    ## Session
    Return session metadata computed from aind-metadata-mapper.
    """

    job_response: JobResponse = await session_json_api_instance.get_session(
        job_settings=job_settings
    )
    json_response = JSONResponse(
        status_code=job_response.status_code,
        content=({"message": job_response.message, "data": job_response.data}),
    )
    return json_response
