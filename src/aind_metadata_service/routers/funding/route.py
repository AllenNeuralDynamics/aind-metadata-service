"""Module to handle funding endpoint responses"""

import json
import logging
from typing import Any, Dict, List, Union

from aind_data_schema.core.data_description import Funding
from aind_smartsheet_api.client import SmartsheetClient
from fastapi import APIRouter, Depends, Path, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from aind_metadata_service.backends.smartsheet.configs import (
    SmartsheetAppConfigs,
    get_settings,
)
from aind_metadata_service.backends.smartsheet.handler import SessionHandler
from aind_metadata_service.backends.smartsheet.models import FundingModel
from aind_metadata_service.backends.smartsheet.session import get_session
from aind_metadata_service.responses import (
    InternalServerError,
    Message,
    NoDataFound,
)
from aind_metadata_service.routers.funding.mapper import Mapper

router = APIRouter()


class FundingResponse(Message):
    """Valid Subject response"""

    message: str = "Valid Model"
    data: Funding


class InvalidFundingResponse(Message):
    """Invalid Subject response"""

    message: str
    data: Funding


class MultipleItemsFound(Message):
    """Multiple Items Found response"""

    message: str = "Multiple Items Found"
    data: List[Union[Funding, Dict[str, Any]]]


@router.get(
    "/funding/{project_name}",
    response_model=FundingResponse,
    responses={
        status.HTTP_300_MULTIPLE_CHOICES: {"model": MultipleItemsFound},
        status.HTTP_404_NOT_FOUND: {"model": NoDataFound},
        status.HTTP_406_NOT_ACCEPTABLE: {"model": InvalidFundingResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerError},
    },
)
async def get_funding(
    project_name: str = Path(..., examples=["Cell Type LUT"]),
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
        parsed_sheet: List[FundingModel] = handler.get_parsed_sheet(
            sheet_id=settings.funding_id, model=FundingModel
        )
        funding_info_list = handler.get_project_funding_info(
            parsed_sheet, project_name=project_name
        )
        if len(funding_info_list) == 0:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.loads(NoDataFound().model_dump_json()),
            )
        else:
            funding_info = [
                Mapper(funding_model=f).map_to_funding()
                for f in funding_info_list
            ]
            if len(funding_info) == 1:
                funding = funding_info[0]
                try:
                    Funding.model_validate(funding.model_dump(warnings="none"))
                    return FundingResponse(data=funding)
                except ValidationError as e:
                    errors = e.json()
                    return JSONResponse(
                        status_code=status.HTTP_406_NOT_ACCEPTABLE,
                        content=json.loads(
                            InvalidFundingResponse(
                                message=f"Validation errors: {errors}",
                                data=funding,
                            ).model_dump_json(warnings="none")
                        ),
                    )
            else:
                return JSONResponse(
                    status_code=status.HTTP_300_MULTIPLE_CHOICES,
                    content=json.loads(
                        MultipleItemsFound(data=funding_info).model_dump_json(
                            warnings="none"
                        )
                    ),
                )
    except Exception as e:
        logging.error(f"An error occurred: {e.args}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.loads(InternalServerError().model_dump_json()),
        )
