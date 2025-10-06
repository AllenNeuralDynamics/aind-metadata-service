"""Module to handle subject endpoints"""

import logging
from fastapi import APIRouter, Depends, Path

from aind_metadata_service_server.mappers.subject import SubjectMapper
from aind_metadata_service_server.response_handler import (
    ModelResponse,
    StatusCodes,
)
from aind_metadata_service_server.sessions import (
    get_labtracks_api_instance,
    get_mgi_api_instance,
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
    labtracks_api_instance=Depends(get_labtracks_api_instance),
    mgi_api_instance=Depends(get_mgi_api_instance),
):
    """
    ## Subject
    Return Subject metadata.
    """
    labtracks_response = await labtracks_api_instance.get_subject(
        subject_id, _request_timeout=10
    )

    mappers = [
        SubjectMapper(labtracks_subject=labtracks_subject)
        for labtracks_subject in labtracks_response
    ]

    for mapper in mappers:
        mgi_info = []
        allele_names = mapper.get_allele_names_from_genotype()
        for allele_name in allele_names:
            api_response = await mgi_api_instance.get_allele_info(
                allele_name=allele_name, _request_timeout=10
            )
            mgi_info.extend(api_response)
        mapper.mgi_info = mgi_info

    subjects = [mapper.map_to_aind_subject() for mapper in mappers]
    response_handler = ModelResponse(
        aind_models=subjects, status_code=StatusCodes.DB_RESPONDED
    )
    response = response_handler.map_to_json_response()
    return response
