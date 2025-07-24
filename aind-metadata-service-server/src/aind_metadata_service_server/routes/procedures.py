"""Module to handle subject endpoints"""

from fastapi import APIRouter, Depends, Path

from aind_metadata_service_server.mappers.procedures import ProceduresMapper
from aind_metadata_service_server.mappers.protocol import ProtocolsIntegrator
from aind_metadata_service_server.response_handler import (
    ModelResponse,
    StatusCodes,
)
from aind_metadata_service_server.sessions import (
    get_labtracks_api_instance,
    get_sharepoint_api_instance,
    get_slims_api_instance,
    get_smartsheet_api_instance,
    get_tars_api_instance,
)

router = APIRouter()


@router.get("/procedures/{subject_id}")
async def get_procedures(
    subject_id: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "Subject ID Example 1",
                "description": "Example subject ID for Procedures",
                "value": "632269",
            },
            "example_nsb2019": {
                "summary": "Subject ID Example 2",
                "description": "Example subject ID for Procedures",
                "value": "656374",
            },
            "example_nsb2023": {
                "summary": "Subject ID Example 3",
                "description": "Example subject ID for Procedures",
                "value": "657849",
            },
        },
    ),
    # labtracks_api_instance=Depends(get_labtracks_api_instance),
    sharepoint_api_instance=Depends(get_sharepoint_api_instance),
    slims_api_instance=Depends(get_slims_api_instance),
    smartsheet_api_instance=Depends(get_smartsheet_api_instance),
    tars_api_instance=Depends(get_tars_api_instance),
):
    """
    ## Procedures
    Return Procedure metadata.
    """
    # labtracks_response = await labtracks_api_instance.get_tasks(
    #     subject_id, _request_timeout=10
    # )
    nsb_2019_response = await sharepoint_api_instance.get_nsb2019(
        subject_id, _request_timeout=10
    )
    nsb_2023_response = await sharepoint_api_instance.get_nsb2023(
        subject_id, _request_timeout=10
    )
    nsb_present_response = await sharepoint_api_instance.get_nsb_present(
        subject_id, _request_timeout=10
    )
    las_2020_response = await sharepoint_api_instance.get_las2020(
        subject_id, _request_timeout=10
    )
    slims_wr_response = await slims_api_instance.get_water_restriction_data(
        subject_id, _request_timeout=10
    )
    slims_histology_response = await slims_api_instance.get_histology_data(
        subject_id, _request_timeout=10
    )
    smartsheet_perfusion_response = await smartsheet_api_instance.get_perfusions(
        subject_id, _request_timeout=10
    )
    mapper = ProceduresMapper(
        # labtracks_tasks=labtracks_response,
        nsb_2019=nsb_2019_response,
        nsb_2023=nsb_2023_response,
        nsb_present=nsb_present_response,
        las_2020=las_2020_response,
        slims_wr=slims_wr_response,
        slims_histology=slims_histology_response,
        smartsheet_perfusion=smartsheet_perfusion_response,
    )
    procedures = mapper.map_responses_to_aind_procedures(subject_id)
    if procedures is None:
        return ModelResponse.no_data_found_error_response()
    
    protocol_names = mapper.get_protocols_list(procedures.subject_procedures)

    # Fetch protocol info for each protocol name
    protocols_mapping = {}
    for protocol_name in protocol_names:
        protocol_records = await smartsheet_api_instance.get_protocols(protocol_name=protocol_name)
        protocols_mapping[protocol_name] = protocol_records[0] if protocol_records else None

    # Integrate protocols into procedures
    procedures = mapper.integrate_protocols_into_aind_procedures(procedures, protocols_mapping)
    response_handler = ModelResponse(
        aind_models=[procedures], status_code=StatusCodes.DB_RESPONDED
    )
    response = response_handler.map_to_json_response()
    return response
