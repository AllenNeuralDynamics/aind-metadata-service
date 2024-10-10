"""Module to define shared response models"""

from typing import Any, Dict, Literal

from pydantic import BaseModel


class Message(BaseModel):
    """A generic message response with a data container."""

    message: str
    data: Any


class InvalidModelResponse(Message):
    """A response when data we are returning is not a valid aind core model."""

    data: Dict[str, Any]


class InternalServerError(Message):
    """A response when an unexpected error occurred."""

    message: Literal["Internal Server Error"] = "Internal Server Error"
    data: Literal[None] = None


class NoDataFound(Message):
    """A response for when data is found for the given input."""

    message: Literal["No Data Found"] = "No Data Found"
    data: Literal[None] = None
