"""Module to handle subject endpoint responses"""

import json
import logging
from typing import Any, Dict, List, Union

from aind_data_schema.core.subject import Subject
from fastapi import APIRouter, Depends, Path, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlmodel import Session

from aind_metadata_service.backends.labtracks.handler import SessionHandler
from aind_metadata_service.backends.labtracks.session import get_session
from aind_metadata_service.responses import (
    InternalServerError,
    Message,
    NoDataFound,
)
from aind_metadata_service.routers.subject.mapper import Mapper

router = APIRouter()


class SubjectResponse(Message):
    """Valid Subject response"""

    message: str = "Valid Model"
    data: Subject


class InvalidSubjectResponse(Message):
    """Invalid Subject response"""

    message: str
    data: Subject


class MultipleItemsFound(Message):
    """Multiple Items Found response"""

    message: str = "Multiple Items Found"
    data: List[Union[Subject, Dict[str, Any]]]


@router.get(
    "/subject/{subject_id}",
    response_model=SubjectResponse,
    responses={
        status.HTTP_300_MULTIPLE_CHOICES: {"model": MultipleItemsFound},
        status.HTTP_404_NOT_FOUND: {"model": NoDataFound},
        status.HTTP_406_NOT_ACCEPTABLE: {"model": InvalidSubjectResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerError},
    },
)
async def get_subject(
    subject_id: str = Path(..., examples=["632269"]),
    session: Session = Depends(get_session),
):
    """
    ## Subject metadata
    Retrieves subject information from LabTracks.
    """
    try:
        lab_tracks_subjects = SessionHandler(session=session).get_subject_view(
            subject_id=subject_id
        )
        print("LB:", lab_tracks_subjects)
        if len(lab_tracks_subjects) == 0:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=json.loads(NoDataFound().model_dump_json()),
            )
        else:
            subjects = [
                Mapper(lab_tracks_subject=s).map_to_subject()
                for s in lab_tracks_subjects
            ]
            if len(subjects) == 1:
                subject = subjects[0]
                try:
                    Subject.model_validate(subject.model_dump())
                    return SubjectResponse(data=subject)
                except ValidationError as e:
                    errors = e.json()
                    return JSONResponse(
                        status_code=status.HTTP_406_NOT_ACCEPTABLE,
                        content=json.loads(
                            InvalidSubjectResponse(
                                message=f"Validation errors: {errors}",
                                data=subject,
                            ).model_dump_json()
                        ),
                    )
            else:
                return JSONResponse(
                    status_code=status.HTTP_300_MULTIPLE_CHOICES,
                    content=json.loads(
                        MultipleItemsFound(data=subjects).model_dump_json()
                    ),
                )
    except Exception as e:
        logging.error(f"An error occurred: {e.args}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=json.loads(InternalServerError().model_dump_json()),
        )
