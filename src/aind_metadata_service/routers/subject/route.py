import logging

from fastapi import APIRouter, Path, Depends

from aind_data_schema.core.subject import Subject
from fastapi import status
from pydantic import ValidationError

from aind_metadata_service.backends.labtracks.session import get_session
from aind_metadata_service.backends.labtracks.handler import SessionHandler
from aind_metadata_service.routers.subject.mapper import Mapper
from sqlmodel import Session
from typing import List, Dict, Any, Union
from aind_metadata_service.responses import (
    Message,
    InternalServerError,
    NoDataFound,
)
from fastapi.responses import JSONResponse

router = APIRouter()


class SubjectResponse(Message):
    message: str = "Valid Model"
    data: Subject


class InvalidSubjectResponse(Message):
    message: str
    data: Dict[str, Any]


class MultipleItemsFound(Message):
    message: str = "Multiple Items Found."
    data: List[Union[Subject, Dict[str, Any]]]


@router.get(
    "/subject/{subject_id}",
    response_model=Subject,
    responses={
        status.HTTP_300_MULTIPLE_CHOICES: {"model": MultipleItemsFound},
        status.HTTP_404_NOT_FOUND: {"model": NoDataFound},
        status.HTTP_406_NOT_ACCEPTABLE: {"model": InvalidSubjectResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": InternalServerError},
    },
)
async def get_subject(
    subject_id: str = Path(..., example="632269"),
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
        if len(lab_tracks_subjects) == 0:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=NoDataFound().model_dump_json(),
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
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content=SubjectResponse(data=subject),
                    )
                except ValidationError as e:
                    errors = e.json()
                    return JSONResponse(
                        status_code=status.HTTP_406_NOT_ACCEPTABLE,
                        content=InvalidSubjectResponse(
                            message=f"Validation errors: {errors}",
                            data=subject,
                        ),
                    )
            else:
                return JSONResponse(
                    status_code=status.HTTP_300_MULTIPLE_CHOICES,
                    content=MultipleItemsFound(data=subjects),
                )
    except Exception as e:
        logging.error(f"An error occurred: {e.args}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=InternalServerError().model_dump_json(),
        )
