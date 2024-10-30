"""Module to handle perfusions endpoint responses"""

import json
import logging
from typing import Any, Dict, List, Union

from aind_data_schema.core.procedures import Surgery
from aind_smartsheet_api.client import SmartsheetClient
from fastapi import APIRouter, Depends, Path, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from aind_metadata_service.backends.smartsheet.configs import (
    SmartsheetAppConfigs,
    get_settings,
)
from aind_metadata_service.backends.smartsheet.handler import SessionHandler
from aind_metadata_service.backends.smartsheet.models import PerfusionsModel
from aind_metadata_service.backends.smartsheet.session import get_session
from aind_metadata_service.responses import (
    InternalServerError,
    Message,
    NoDataFound,
)
from aind_metadata_service.routers.perfusions.mapper import Mapper

router = APIRouter()


class PerfusionsResponse(Message):
    """Valid Subject response"""

    message: str = "Valid Model"
    data: Surgery


class InvalidPerfusionsResponse(Message):
    """Invalid Perfusions response"""

    message: str
    data: Surgery


class MultipleItemsFound(Message):
    """Multiple Items Found response"""

    message: str = "Multiple Items Found"
    data: List[Union[Surgery, Dict[str, Any]]]


@router.get(
    "/perfusions/{subject_id}",
    response_model=PerfusionsResponse,
    responses={
        status.HTTP_300_MULTIPLE_CHOICES: {"model": MultipleItemsFound},
        status.HTTP_404_NOT_FOUND: {"model": NoDataFound},
        status.HTTP_406_NOT_ACCEPTABLE: {"model": InvalidPerfusionsResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerError},
    },
)
async def get_funding(
    subject_id: str = Path(..., examples=["689418"]),
    session: SmartsheetClient = Depends(get_session),
    settings: SmartsheetAppConfigs = Depends(get_settings),
):
    """
    ## Funding metadata
    Retrieves funding information from SmartSheet for a project name.
    """
    try:
        handler = SessionHandler(session=session)
        # TODO: Pull sheet from cache
        parsed_sheet: List[PerfusionsModel] = handler.get_parsed_sheet(
            sheet_id=settings.perfusions_id, model=PerfusionsModel
        )
        perfusions_list = handler.get_perfusions_info(
            parsed_sheet, subject_id=subject_id
        )
        if len(perfusions_list) == 0:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.loads(NoDataFound().model_dump_json()),
            )
        else:
            perfusions_info = [
                Mapper(perfusions_model=p).map_to_perfusions()
                for p in perfusions_list
            ]
            if len(perfusions_info) == 1:
                perfusions = perfusions_info[0]
                try:
                    Surgery.model_validate(
                        perfusions.model_dump(warnings="none")
                    )
                    return PerfusionsResponse(data=perfusions)
                except ValidationError as e:
                    errors = e.json()
                    return JSONResponse(
                        status_code=status.HTTP_406_NOT_ACCEPTABLE,
                        content=json.loads(
                            InvalidPerfusionsResponse(
                                message=f"Validation errors: {errors}",
                                data=perfusions,
                            ).model_dump_json(warnings="none")
                        ),
                    )
            else:
                return JSONResponse(
                    status_code=status.HTTP_300_MULTIPLE_CHOICES,
                    content=json.loads(
                        MultipleItemsFound(
                            data=perfusions_info
                        ).model_dump_json(warnings="none")
                    ),
                )
    except Exception as e:
        logging.error(f"An error occurred: {e.args}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.loads(InternalServerError().model_dump_json()),
        )
