"""Module to handle subject endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Path

from aind_metadata_service_server.mappers.procedures import ProceduresMapper
from aind_metadata_service_server.mappers.injection_materials import (
    InjectionMaterialsMapper,
)
from aind_metadata_service_server.mappers.responses import map_to_response
from aind_metadata_service_server.sessions import (
    get_labtracks_api_instance,
    get_sharepoint_api_instance,
    get_smartsheet_api_instance,
    get_tars_api_instance,
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
        },
    ),
    labtracks_api_instance=Depends(get_labtracks_api_instance),
    sharepoint_api_instance=Depends(get_sharepoint_api_instance),
    smartsheet_api_instance=Depends(get_smartsheet_api_instance),
    tars_api_instance=Depends(get_tars_api_instance),
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
    smartsheet_perfusion_response = (
        await smartsheet_api_instance.get_perfusions(
            subject_id, _request_timeout=10
        )
    )
    mapper = ProceduresMapper(
        labtracks_tasks=labtracks_response,
        las_2020=las_2020_response,
        nsb_2019=nsb_2019_response,
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
        viruses = mapper.get_virus_strains(procedures)
    tars_mapping = {}
    for virus_strain in viruses:
        tars_prep_lot_response = await tars_api_instance.get_viral_prep_lots(
            lot=virus_strain, _request_timeout=10
        )
        tars_mappers = [
            InjectionMaterialsMapper(tars_prep_lot_data=prep_lot_data)
            for prep_lot_data in tars_prep_lot_response
        ]
        for tars_mapper in tars_mappers:
            virus_id = tars_mapper.virus_id
            if virus_id:
                virus_response = await tars_api_instance.get_viruses(
                    name=virus_id, _request_timeout=10
                )
                tars_mapper.tars_virus_data = virus_response
            tars_mapping[virus_strain] = (
                tars_mapper.map_to_viral_material_information()
            )
        return map_to_response(procedures)
