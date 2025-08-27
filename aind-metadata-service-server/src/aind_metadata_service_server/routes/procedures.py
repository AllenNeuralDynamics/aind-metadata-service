"""Module to handle subject endpoints"""

from fastapi import APIRouter, Depends, Path, HTTPException

from aind_metadata_service_server.mappers.procedures import ProceduresMapper

from aind_metadata_service_server.sessions import (
    get_labtracks_api_instance,
    get_sharepoint_api_instance,
) 

router = APIRouter()


@router.get("/api/v2/procedures/{subject_id}")
async def get_procedures(
    subject_id: str = Path(
        ...,
        openapi_examples={
            "example1": {
                "summary": "Subject ID Example 1",
                "description": "Example subject ID for Procedures",
                "value": "823508",
            },
        },
    ),
    labtracks_api_instance=Depends(get_labtracks_api_instance),
    sharepoint_api_instance=Depends(get_sharepoint_api_instance),
):
    """
    ## Procedures
    Return Procedure metadata.
    """
    labtracks_response = await labtracks_api_instance.get_tasks(
        subject_id, _request_timeout=10
    )
    las_2020_response = await sharepoint_api_instance.get_las2020(
        subject_id, _request_timeout=20
    )
    mapper = ProceduresMapper(
        labtracks_tasks=labtracks_response,
        las_2020=las_2020_response,
    )
    procedures = mapper.map_responses_to_aind_procedures(subject_id)
    if not procedures:
        raise HTTPException(status_code=404, detail="Not found")
    else:
        return procedures