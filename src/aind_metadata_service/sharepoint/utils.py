"""Utility methods useful for parsing sharepoint models"""

from typing import Any, Optional

from pydantic import ValidationError
from pydantic_core.core_schema import ValidatorFunctionWrapHandler


def optional_enum(
    v: Any, handler: ValidatorFunctionWrapHandler
) -> Optional[Any]:
    """If an enum value does not exist, will use None instead"""
    try:
        validated_v = handler(v)
        return validated_v
    except ValidationError:
        return None
