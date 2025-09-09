"""Module to handle subject endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Path

from aind_metadata_service_server.mappers.procedures import ProceduresMapper
from aind_metadata_service_server.mappers.responses import map_to_response
from aind_metadata_service_server.sessions import (
    get_labtracks_api_instance,
    get_sharepoint_api_instance,
    get_smartsheet_api_instance,
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
            "example2": {
                "summary": "Subject ID Example 2",
                "description": "Example subject ID for Procedures",
                "value": "632269",
            },
            "example3": {
                "summary": "Subject ID Example 3",
                "description": "Example subject ID for Procedures",
                "value": "656374",
            },
        },
    ),
    labtracks_api_instance=Depends(get_labtracks_api_instance),
    sharepoint_api_instance=Depends(get_sharepoint_api_instance),
    smartsheet_api_instance=Depends(get_smartsheet_api_instance),
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
    nsb_2019_response = await sharepoint_api_instance.get_nsb2019(
        subject_id, _request_timeout=10
    )
    nsb_2023_response = await sharepoint_api_instance.get_nsb2023(
        subject_id, _request_timeout=10
    )
    nsb_present_response = await sharepoint_api_instance.get_nsb_present(
        subject_id, _request_timeout=10
    )
    smartsheet_perfusion_response = (
        await smartsheet_api_instance.get_perfusions(
            subject_id, _request_timeout=10
        )
    )
    mapper = ProceduresMapper(
        labtracks_tasks=labtracks_response,
        las_2020=las_2020_response,
        nsb_2019=nsb_2019_response,
        nsb_2023=nsb_2023_response,
        nsb_present=nsb_present_response,
        smartsheet_perfusion=smartsheet_perfusion_response,
    )
    procedures = mapper.map_responses_to_aind_procedures(subject_id)
    if not procedures:
        raise HTTPException(status_code=404, detail="Not found")
    else:
        # integrate protocols from smartsheet
        protocol_names = mapper.get_protocols_list(procedures)
        protocols_mapping = {}
        for protocol_name in protocol_names:
            protocol_records = await smartsheet_api_instance.get_protocols(
                protocol_name=protocol_name
            )
            protocols_mapping[protocol_name] = (
                protocol_records[0] if protocol_records else None
            )
        procedures = mapper.integrate_protocols_into_aind_procedures(
            procedures, protocols_mapping
        )
        return map_to_response(procedures)
