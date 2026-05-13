"""Module to handle subject endpoints"""

from fastapi import APIRouter, Depends, Path

from aind_metadata_service_server.mappers.injection_materials import TarsMapper
from aind_metadata_service_server.mappers.procedures import ProceduresMapper
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
            "example1": {
                "summary": "Subject ID Example 1",
                "description": "Example subject ID for Procedures",
                "value": "632269",
            },
            "example2": {
                "summary": "Subject ID Example 2",
                "description": "Example subject ID for Procedures",
                "value": "656374",
            },
            "example3": {
                "summary": "Subject ID Example 3",
                "description": "Example subject ID for Procedures",
                "value": "804998",
            },
        },
    ),
    labtracks_api_instance=Depends(get_labtracks_api_instance),
    sharepoint_api_instance=Depends(get_sharepoint_api_instance),
    slims_api_instance=Depends(get_slims_api_instance),
    smartsheet_api_instance=Depends(get_smartsheet_api_instance),
    tars_api_instance=Depends(get_tars_api_instance),
):
    """
    ## Procedures
    Return Procedure metadata.
    """
    labtracks_response = await labtracks_api_instance.get_tasks(
        subject_id, _request_timeout=20
    )
    nsb_2019_response = await sharepoint_api_instance.get_nsb2019(
        subject_id, _request_timeout=20
    )
    nsb_2023_response = await sharepoint_api_instance.get_nsb2023(
        subject_id, _request_timeout=20
    )
    nsb_present_response = await sharepoint_api_instance.get_nsb_present(
        subject_id, _request_timeout=20
    )
    las_2020_response = await sharepoint_api_instance.get_las2020(
        subject_id, _request_timeout=30
    )
    slims_wr_response = await slims_api_instance.get_water_restriction_data(
        subject_id, _request_timeout=240
    )
    slims_histology_response = await slims_api_instance.get_histology_data(
        subject_id, _request_timeout=240
    )
    smartsheet_perfusion_response = (
        await smartsheet_api_instance.get_perfusions(
            subject_id, _request_timeout=20
        )
    )
    mapper = ProceduresMapper(
        labtracks_tasks=labtracks_response,
        nsb_2019=nsb_2019_response,
        nsb_2023=nsb_2023_response,
        nsb_present=nsb_present_response,
        las_2020=las_2020_response,
        slims_water_restriction=slims_wr_response,
        slims_histology=slims_histology_response,
        smartsheet_perfusion=smartsheet_perfusion_response,
    )
    procedures = mapper.map_responses_to_aind_procedures(subject_id)
    if procedures is None:
        no_data_response = ModelResponse.no_data_found_error_response()
        return no_data_response.map_to_json_response()

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

    # integrate injection materials from TARS
    # TODO: Optimize this by linking separate API calls in TARS service
    viruses = mapper.get_virus_strains(procedures)
    tars_mapping = {}
    for virus_strain in viruses:
        tars_prep_lot_response = await tars_api_instance.get_viral_prep_lots(
            lot=virus_strain, _request_timeout=10
        )
        tars_mappers = [
            TarsMapper(prep_lot_data=prep_lot_data)
            for prep_lot_data in tars_prep_lot_response
        ]
        for tars_mapper in tars_mappers:
            virus_id = tars_mapper.virus_id
            if virus_id:
                virus_response = await tars_api_instance.get_viruses(
                    name=virus_id, _request_timeout=10
                )
                tars_mapper.virus_data = virus_response
            tars_mapping[virus_strain] = (
                tars_mapper.map_to_viral_material_information()
            )

    procedures = mapper.integrate_injection_materials_into_aind_procedures(
        procedures, tars_mapping
    )
    response_handler = ModelResponse(
        aind_models=[procedures], status_code=StatusCodes.DB_RESPONDED
    )
    response = response_handler.map_to_json_response()
    return response
