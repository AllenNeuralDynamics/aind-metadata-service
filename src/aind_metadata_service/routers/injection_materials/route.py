"""Module to handle injection_materials endpoint responses"""

import json
import logging

from aind_data_schema.core.procedures import ViralMaterial
from fastapi import APIRouter, Depends, Path, status
from fastapi.responses import JSONResponse
from fastapi_cache.decorator import cache
from pydantic import ValidationError
from pydash import get as get_or_else
from requests import Session

from aind_metadata_service.backends.tars.configs import Settings, get_settings
from aind_metadata_service.backends.tars.handler import SessionHandler
from aind_metadata_service.backends.tars.session import get_session
from aind_metadata_service.responses import (
    InternalServerError,
    Message,
    NoDataFound,
)
from aind_metadata_service.routers.injection_materials.mapper import Mapper

router = APIRouter()


class ViralMaterialResponse(Message):
    """Valid Subject response"""

    message: str = "Valid Model"
    data: ViralMaterial


class InvalidViralMaterialResponse(Message):
    """Invalid ViralMaterial response"""

    message: str
    data: ViralMaterial


@cache(expire=3500)
async def get_access_token(settings: Settings) -> str:
    """
    Get access token from either Azure or cache. Token is valid for 60 minutes.
    We set cache ttl to 3500 seconds.
    Parameters
    ----------
    settings : Settings

    Returns
    -------
    str

    """
    token, _ = settings.get_bearer_token()
    return token


@router.get(
    "/injection_materials/{prep_lot_id}",
    response_model=ViralMaterialResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": NoDataFound},
        status.HTTP_406_NOT_ACCEPTABLE: {
            "model": InvalidViralMaterialResponse
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerError},
    },
)
async def get_injection_materials(
    prep_lot_id: str = Path(..., examples=["VT3214g"]),
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_settings),
):
    """
    ## Perfusions metadata
    Retrieves perfusions information from SmartSheet for a subject_id.
    """
    try:
        bearer_token = await get_access_token(settings=settings)
        handler = SessionHandler(
            session=session, bearer_token=bearer_token, settings=settings
        )
        prep_lot_data = handler.get_prep_lot_data(prep_lot_id=prep_lot_id)
        if len(prep_lot_data) == 0:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.loads(NoDataFound().model_dump_json()),
            )
        else:
            # For now, we've restricted the TARS get to return only object
            first_prep_lot_data = prep_lot_data[0]
            mapper = Mapper(prep_lot_data=first_prep_lot_data)
            prep_lot_viral_aliases = get_or_else(
                first_prep_lot_data, "viralPrep.virus.aliases", []
            )
            viral_aliases = mapper.map_virus_aliases(prep_lot_viral_aliases)
            if (
                viral_aliases.plasmid_name is not None
                and viral_aliases.full_genome_name is None
            ):
                molecule_data = handler.get_molecule_data(
                    plasmid_name=viral_aliases.plasmid_name
                )
                if len(molecule_data) > 0:
                    full_genome_name = mapper.map_full_genome_name(
                        plasmid_name=viral_aliases.plasmid_name,
                        genome_name=viral_aliases.full_genome_name,
                        molecule_aliases=molecule_data[0].aliases,
                    )
                    viral_aliases.full_genome_name = full_genome_name
            viral_materials = mapper.map_to_viral_material(viral_aliases)
            try:
                ViralMaterial.model_validate(
                    viral_materials.model_dump(warnings="none")
                )
                return ViralMaterialResponse(data=viral_materials)
            except ValidationError as e:
                errors = e.json()
                return JSONResponse(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    content=json.loads(
                        InvalidViralMaterialResponse(
                            message=f"Validation errors: {errors}",
                            data=viral_materials,
                        ).model_dump_json(warnings="none")
                    ),
                )
    except Exception as e:
        logging.error(f"An error occurred: {e.args}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.loads(InternalServerError().model_dump_json()),
        )
