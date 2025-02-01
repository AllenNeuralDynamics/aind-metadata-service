"""Module to handle project names endpoint responses"""

import json
import logging
from typing import List

from aind_smartsheet_api.client import SmartsheetClient
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

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

router = APIRouter()


class ProjectNamesResponse(Message):
    """Valid Project Names response"""

    message: str = "Success"
    data: List[str]


@router.get(
    "/project_names",
    response_model=ProjectNamesResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": NoDataFound},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerError},
    },
)
async def get_project_names(
    session: SmartsheetClient = Depends(get_session),
    settings: SmartsheetAppConfigs = Depends(get_settings),
):
    """
    ## Project Names
    Retrieves project names from Funding Smartsheet.
    """
    try:
        handler = SessionHandler(session=session)
        # TODO: Pull sheet from cache
        parsed_sheet: List[FundingModel] = handler.get_parsed_sheet(
            sheet_id=settings.funding_id, model=FundingModel
        )
        project_names = handler.get_project_names(parsed_sheet)
        if len(project_names) == 0:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.loads(NoDataFound().model_dump_json()),
            )
        else:
            return ProjectNamesResponse(data=project_names)

    except Exception as e:
        logging.error(f"An error occurred: {e.args}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.loads(InternalServerError().model_dump_json()),
        )
