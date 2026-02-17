"""Module to handle subject endpoints"""

from asyncio import gather

from fastapi import APIRouter, Depends, HTTPException, Path

from aind_metadata_service_server.mappers.injection_materials import (
    InjectionMaterialsMapper,
)
from aind_metadata_service_server.mappers.procedures import ProceduresMapper
from aind_metadata_service_server.mappers.responses import map_to_response
from aind_metadata_service_server.sessions import (
    get_labtracks_api_instance,
    get_sharepoint_api_instance,
    get_slims_api_instance,
    get_smartsheet_api_instance,
    get_tars_api_instance,
)

router = APIRouter()


@router.get(
    "/api/v2/procedures/{subject_id}",
    responses={
        400: {
            "description": "Validation error in response model.",
            "content": {
                "application/json": {
                    "example": {"detail": "Validation error in response model."}
                }
            },
        },
        404: {"description": "Not found"},
    },
)
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
            "example4": {
                "summary": "Subject ID Example 4",
                "description": "Example subject ID for Procedures",
                "value": "762287",
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
    tasks = list()
    tasks.append(
        labtracks_api_instance.get_tasks(subject_id, _request_timeout=20)
    )
    tasks.append(
        sharepoint_api_instance.get_las2020(subject_id, _request_timeout=30)
    )
    tasks.append(
        sharepoint_api_instance.get_nsb2019(subject_id, _request_timeout=20)
    )
    tasks.append(
        sharepoint_api_instance.get_nsb2023(subject_id, _request_timeout=20)
    )
    tasks.append(
        sharepoint_api_instance.get_nsb_present(
            subject_id, _request_timeout=20
        )
    )
    tasks.append(
        slims_api_instance.get_water_restriction_data(
            subject_id, _request_timeout=240
        )
    )
    tasks.append(
        slims_api_instance.get_histology_data(subject_id, _request_timeout=240)
    )
    tasks.append(
        smartsheet_api_instance.get_perfusions(subject_id, _request_timeout=20)
    )
    (
        labtracks_response,
        las_2020_response,
        nsb_2019_response,
        nsb_2023_response,
        nsb_present_response,
        slims_wr_response,
        slims_histology_response,
        smartsheet_perfusion_response,
    ) = await gather(*tasks)

    mapper = ProceduresMapper(
        labtracks_tasks=labtracks_response,
        las_2020=las_2020_response,
        nsb_2019=nsb_2019_response,
        nsb_2023=nsb_2023_response,
        nsb_present=nsb_present_response,
        slims_water_restriction=slims_wr_response,
        slims_histology=slims_histology_response,
        smartsheet_perfusion=smartsheet_perfusion_response,
    )
    procedures = mapper.map_responses_to_aind_procedures(subject_id)
    if not procedures:
        raise HTTPException(status_code=404, detail="Not found")

    # integrate protocols from smartsheet
    protocol_names = mapper.get_protocols_list(procedures)
    protocol_tasks = [
        smartsheet_api_instance.get_protocols(protocol_name=protocol_name)
        for protocol_name in protocol_names
    ]
    protocol_results = await gather(*protocol_tasks) if protocol_tasks else []
    protocols_mapping = {
        name: (records[0] if records else None)
        for name, records in zip(protocol_names, protocol_results)
    }

    procedures = mapper.integrate_protocols_into_aind_procedures(
        procedures, protocols_mapping
    )

    # integrate injection materials from tars
    viruses = mapper.get_virus_strains(procedures)
    viral_prep_tasks = [
        tars_api_instance.get_viral_prep_lots(
            lot=virus_strain, _request_timeout=10
        )
        for virus_strain in viruses
    ]
    viral_prep_results = (
        await gather(*viral_prep_tasks) if viral_prep_tasks else []
    )
    virus_mappers_by_strain = {}
    virus_ids_to_fetch = []
    virus_id_to_strain_mapper = []

    for virus_strain, tars_prep_lot_response in zip(
        viruses, viral_prep_results
    ):
        tars_mappers = [
            InjectionMaterialsMapper(tars_prep_lot_data=prep_lot_data)
            for prep_lot_data in tars_prep_lot_response
        ]
        virus_mappers_by_strain[virus_strain] = tars_mappers

        for tars_mapper in tars_mappers:
            if tars_mapper.virus_id:
                virus_ids_to_fetch.append(tars_mapper.virus_id)
                virus_id_to_strain_mapper.append((virus_strain, tars_mapper))

    if virus_ids_to_fetch:
        virus_tasks = [
            tars_api_instance.get_viruses(name=virus_id, _request_timeout=10)
            for virus_id in virus_ids_to_fetch
        ]
        virus_responses = await gather(*virus_tasks)
        for (virus_strain, tars_mapper), virus_response in zip(
            virus_id_to_strain_mapper, virus_responses
        ):
            tars_mapper.tars_virus_data = virus_response

    tars_mapping = {}
    for virus_strain, mappers in virus_mappers_by_strain.items():
        if mappers:
            tars_mapping[virus_strain] = mappers[
                0
            ].map_to_viral_material_information()
        else:
            tars_mapping[virus_strain] = None

    procedures = mapper.integrate_injection_materials_into_aind_procedures(
        procedures, tars_mapping
    )
    return map_to_response(procedures)
