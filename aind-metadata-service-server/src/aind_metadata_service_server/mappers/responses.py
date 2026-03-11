"""Validates aind models and maps to a JSONResponse."""

import logging
import re
import json
from typing import List, Union

from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError


def clean_error_messages(error_json: str) -> str:
    """Remove function-after patterns from pydantic error messages."""
    pattern = r'"function-after\[[^\]]*(?:\[[^\]]*\][^\]]*)*\]",?'
    cleaned = re.sub(pattern, "", error_json)

    return cleaned


def map_to_response(model: Union[BaseModel, List[BaseModel]]) -> JSONResponse:
    """
    Maps a pydantic model to a JSONResponse message. If the model is valid,
    then it will return a 200 status code. If the model is not valid, then it
    will return a 400 status code with the validation errors in the headers
    under the 'X-Error-Message' key.
    """

    try:
        if isinstance(model, list):
            for item in model:
                item.model_validate(item.model_dump())
            content = [item.model_dump(mode="json") for item in model]
        else:
            validate = model.model_validate(model.model_dump())
            content = validate.model_dump(mode="json")
        return JSONResponse(content=content)
    except ValidationError:
        if isinstance(model, list):
            content = [item.model_dump(mode="json") for item in model]
        else:
            content = model.model_dump(mode="json")

        # errors = e.json(include_context=False, include_input=False)
        # errors = clean_error_messages(errors)

        errors = json.dumps({})

        logging.warning(errors)
        return JSONResponse(
            status_code=400,
            content=content,
            headers={"X-Error-Message": errors},
        )
