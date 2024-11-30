"""Module to handle injection_materials endpoint responses"""

import json
import logging
from typing import Any, Dict, List, Union

from fastapi import APIRouter, Depends, Path, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from aind_metadata_service.backends.tars.configs import (
    Settings,
    get_settings,
)

from requests import Session
from aind_data_schema.core.procedures import ViralMaterial
from aind_metadata_service.backends.tars.handler import SessionHandler
from aind_metadata_service.backends.tars.models import (
    PrepLotResponse,
    MoleculeResponse,
)
from aind_metadata_service.backends.tars.session import get_session
from aind_metadata_service.responses import (
    InternalServerError,
    Message,
    NoDataFound,
)
from aind_metadata_service.routers.injection_materials.mapper import Mapper
from fastapi_cache.backends.redis import RedisBackend

router = APIRouter()


class InjectionMaterialsResponse(Message):
    """Valid Subject response"""

    message: str = "Valid Model"
    data: ViralMaterial


class InvalidInjectionMaterialsResponse(Message):
    """Invalid Perfusions response"""

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
    response_model=PrepLotResponse,
    responses={
        # status.HTTP_404_NOT_FOUND: {"model": NoDataFound},
        # status.HTTP_406_NOT_ACCEPTABLE: {"model": InvalidInjectionMaterialsResponse},
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
        prep_lot_response = handler._get_prep_lot_response(prep_lot_id=prep_lot_id)
        return prep_lot_response
    except Exception as e:
        logging.error(f"An error occurred: {e.args}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.loads(InternalServerError().model_dump_json()),
        )
