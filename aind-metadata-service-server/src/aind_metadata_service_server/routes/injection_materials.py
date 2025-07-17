"""Module to handle injection_material endpoints"""

import logging
from typing import List

from fastapi import APIRouter, Depends, Path

from aind_metadata_service_server.mappers.injection_materials import TarsMapper
from aind_metadata_service_server.response_handler import (
    ModelResponse,
    StatusCodes,
)
from aind_metadata_service_server.sessions import (
    get_tars_api_instance
)

router = APIRouter()


@router.get("/tars_injection_material/{prep_lot_number}")
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
    tars_prep_lot_response = await tars_api_instance.get_viral_prep_lots(
        lot=prep_lot_number, _request_timeout=10
    )
    if not tars_prep_lot_response:
        return ModelResponse.no_data_found_error_response().map_to_json_response()
    
    viral_materials = []
    for prep_lot_data in tars_prep_lot_response:
        virus_tars_id = None
        if (prep_lot_data.viral_prep and 
            prep_lot_data.viral_prep.virus and 
            prep_lot_data.viral_prep.virus.aliases):
            virus_tars_id = next(
                (
                    alias.name
                    for alias in prep_lot_data.viral_prep.virus.aliases
                    if alias.is_preferred
                ),
                None,
            )
        if not virus_tars_id:
            logging.warning(f"No virus TARS ID found for prep lot {prep_lot_number}")
            continue
        
        virus_response = await tars_api_instance.get_viruses(
            name=virus_tars_id, _request_timeout=10
        )
        
        if not virus_response or not virus_response[0]:
            logging.warning(f"No virus data found for virus ID {virus_tars_id}")
            continue
        
        mapper = TarsMapper(
            prep_lot_data=prep_lot_data,
            virus_data=virus_response[0],
            virus_tars_id=virus_tars_id,
        )
        
        viral_material = mapper.map_to_viral_material_information()
        viral_materials.append(viral_material)
    
    if not viral_materials:
        return ModelResponse.no_data_found_error_response().map_to_json_response()
    
    response_handler = ModelResponse(
        aind_models=viral_materials, 
        status_code=StatusCodes.DB_RESPONDED
    )
    return response_handler.map_to_json_response()
