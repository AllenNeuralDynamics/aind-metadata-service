from pydantic import BaseModel
from typing import Any, Dict, Literal


class Message(BaseModel):

    message: str
    data: Any


class InvalidModelResponse(Message):
    data: Dict[str, Any]


class InternalServerError(Message):
    message: Literal["Internal Server Error"]
    data: Literal[None]


class NoDataFound(Message):
    message: Literal["No Data Found."]
    data: Literal[None]