"""Module to handle protocols endpoint responses"""

import json
import logging
from typing import Any, Dict, List, Union

from aind_smartsheet_api.client import SmartsheetClient
from fastapi import APIRouter, Depends, Path, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from aind_metadata_service.backends.smartsheet.configs import (
    SmartsheetAppConfigs,
    get_settings,
)
from aind_metadata_service.backends.smartsheet.handler import SessionHandler
from aind_metadata_service.backends.smartsheet.models import ProtocolsModel
from aind_metadata_service.backends.smartsheet.session import get_session
from aind_metadata_service.responses import (
    InternalServerError,
    Message,
    NoDataFound,
)

router = APIRouter()


class ProtocolsResponse(Message):
    """Valid Subject response"""

    message: str = "Valid Model"
    data: ProtocolsModel


class InvalidProtocolsResponse(Message):
    """Invalid Subject response"""

    message: str
    data: ProtocolsModel


class MultipleItemsFound(Message):
    """Multiple Items Found response"""

    message: str = "Multiple Items Found"
    data: List[Union[ProtocolsModel, Dict[str, Any]]]


@router.get(
    "/protocols/{protocol_name}",
    response_model=ProtocolsResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": NoDataFound},
        status.HTTP_406_NOT_ACCEPTABLE: {"model": InvalidProtocolsResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerError},
    },
)
async def get_protocols(
    protocol_name: str = Path(
        ...,
        examples=[
            (
                "Tetrahydrofuran and Dichloromethane Delipidation of a Whole "
                "Mouse Brain"
            )
        ],
    ),
    session: SmartsheetClient = Depends(get_session),
    settings: SmartsheetAppConfigs = Depends(get_settings),
):
    """
    ## Funding metadata
    Retrieves funding information from SmartSheet for a protocol name.
    """
    try:
        handler = SessionHandler(session=session)
        # TODO: Pull sheet from cache
        parsed_sheet: List[ProtocolsModel] = handler.get_parsed_sheet(
            sheet_id=settings.protocols_id, model=ProtocolsModel
        )
        protocols_list = handler.get_protocols_info(
            parsed_sheet, protocol_name=protocol_name
        )
        if len(protocols_list) == 0:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.loads(NoDataFound().model_dump_json()),
            )
        else:
            if len(protocols_list) == 1:
                protocol = protocols_list[0]
                try:
                    ProtocolsModel.model_validate(
                        protocol.model_dump(warnings="none")
                    )
                    return ProtocolsResponse(data=protocol)
                except ValidationError as e:
                    errors = e.json()
                    return JSONResponse(
                        status_code=status.HTTP_406_NOT_ACCEPTABLE,
                        content=json.loads(
                            InvalidProtocolsResponse(
                                message=f"Validation errors: {errors}",
                                data=protocol,
                            ).model_dump_json(warnings="none")
                        ),
                    )
            else:
                return JSONResponse(
                    status_code=status.HTTP_300_MULTIPLE_CHOICES,
                    content=json.loads(
                        MultipleItemsFound(
                            data=protocols_list
                        ).model_dump_json(warnings="none")
                    ),
                )
    except Exception as e:
        logging.error(f"An error occurred: {e.args}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.loads(InternalServerError().model_dump_json()),
        )
