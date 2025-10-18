"""Module to handle injection_material endpoints"""

from typing import List

from aind_tars_service_async_client import PrepLotData
from fastapi import APIRouter, Depends, HTTPException, Path

from aind_metadata_service_server.mappers.injection_materials import (
    InjectionMaterialsMapper,
)
from aind_metadata_service_server.mappers.responses import map_to_response
from aind_metadata_service_server.sessions import get_tars_api_instance

router = APIRouter()


@router.get("/api/v2/tars_injection_materials/{prep_lot_number}")
async def get_injection_materials(
    prep_lot_number: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample prep lot number",
                "description": "Example prep lot number for TARS",
                "value": "VT3214G",
            }
        },
    ),
    tars_api_instance=Depends(get_tars_api_instance),
):
    """
    ## Injection Materials
    Return Injection Materials metadata.
    """
    tars_prep_lot_response: List[PrepLotData] = (
        await tars_api_instance.get_viral_prep_lots(
            lot=prep_lot_number, _request_timeout=10
        )
    )
    mappers = [
        InjectionMaterialsMapper(tars_prep_lot_data=prep_lot_data)
        for prep_lot_data in tars_prep_lot_response
    ]
    for mapper in mappers:
        virus_id = mapper.virus_id
        if virus_id:
            virus_response = await tars_api_instance.get_viruses(
                name=virus_id, _request_timeout=10
            )
            mapper.tars_virus_data = virus_response

    viral_materials = [m.map_to_viral_material_information() for m in mappers]
    if len(viral_materials) == 0:
        raise HTTPException(status_code=404, detail="Not found")
    else:
        return map_to_response(viral_materials)
