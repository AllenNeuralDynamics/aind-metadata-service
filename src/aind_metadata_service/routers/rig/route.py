"""Module to handle rig endpoint responses"""

import json
import logging
from typing import Any, Dict

from aind_slims_api.core import SlimsClient
from fastapi import APIRouter, Depends, Path, status
from fastapi.responses import JSONResponse

from aind_metadata_service.backends.slims.handler import SessionHandler
from aind_metadata_service.backends.slims.session import get_session
from aind_metadata_service.responses import (
    InternalServerError,
    Message,
    NoDataFound,
)

router = APIRouter()


class RigResponse(Message):
    """Valid Rig response"""

    message: str = "Success"
    data: Dict[str, Any]


@router.get(
    "/rig/{rig_id}",
    response_model=RigResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": NoDataFound},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerError},
    },
)
async def get_project_names(
    rig_id: str = Path(..., examples=["323_EPHYS1_OPTO_20240212"]),
    partial_match: bool = False,
    session: SlimsClient = Depends(get_session),
):
    """
    ## Rig
    Retrieves Rig from SLIMS.
    """
    try:
        handler = SessionHandler(session=session)
        # TODO: Cache response
        content = handler.get_instrument_attachment(
            input_id=rig_id, partial_match=partial_match
        )
        if not content:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.loads(NoDataFound().model_dump_json()),
            )
        else:
            return RigResponse(data=content)

    except Exception as e:
        logging.exception(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.loads(InternalServerError().model_dump_json()),
        )
