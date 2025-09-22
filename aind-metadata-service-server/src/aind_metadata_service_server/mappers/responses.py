"""Validates aind models and maps to a JSONResponse."""

import logging

from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError


def map_to_response(model: BaseModel) -> JSONResponse:
    """
    Maps a pydantic model to a JSONResponse message. If the model is valid,
    then it will return a 200 status code. If the model is not valid, then it
    will return a 400 status code with the validation errors in the headers
    under the 'X-Error-Message' key.
    """

    try:
        validate = model.model_validate(model.model_dump())
        content = validate.model_dump(mode="json")
        return JSONResponse(content=content)
    except ValidationError as e:
        content = model.model_dump(mode="json")
        errors = e.json()
        logging.warning(errors)
        return JSONResponse(
            status_code=400,
            content=content,
            headers={"X-Error-Message": errors},
        )
