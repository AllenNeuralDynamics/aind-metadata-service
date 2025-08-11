"""Module to handle subject endpoints"""

from fastapi import APIRouter, Depends, Path

from aind_metadata_service_server.mappers.subject import SubjectMapper
from aind_metadata_service_server.response_handler import (
    ModelResponse,
    StatusCodes,
)
from aind_metadata_service_server.sessions import (
    get_aind_data_schema_v1_session
)

router = APIRouter()


@router.get("/subject/{subject_id}")
async def get_subject(
    subject_id: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample subject ID",
                "description": "Example subject ID for LabTracks",
                "value": "632269",
            }
        },
    ),
    aind_data_schema_v1_session=Depends(get_aind_data_schema_v1_session)
):
    """
    ## Subject
    Return Subject metadata.
    """
    response = await aind_data_schema_v1_session.get(f"subject/{subject_id}")
    return response
