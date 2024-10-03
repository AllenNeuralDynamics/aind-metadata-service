from pydantic import BaseModel
from typing import Any, Dict


class Message(BaseModel):

    message: str
    data: Any


class InvalidModelResponse(Message):
    data: Dict[str, Any]


class InternalServerError(Message):
    message = "Internal Server Error"
    data: Any = None


class NoDataFound(Message):
    message = "No Data Found."
    data: Any = None
