"""Custom exception types for ExaSPIM procedures generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ErrorContext:
    """Structured context attached to ExaspimProceduresError instances.

    Attributes
    ----------
    sheet : str
        The sheet or module where the error originated.
    row_id : int | None
        The Smartsheet row ID, if applicable.
    column : str | None
        The column name involved in the error, if applicable.
    expected : Any | None
        The expected value or description.
    actual : Any | None
        The actual value encountered.
    """

    sheet: str
    row_id: int | None = None
    column: str | None = None
    expected: Any | None = None
    actual: Any | None = None


class ExaspimProceduresError(RuntimeError):
    """Base error for all ExaSPIM procedures generation failures.

    All errors in this package inherit from this class to allow
    blanket exception handling at the top level when desired.
    """

    def __init__(self, message: str, context: ErrorContext | None = None):
        self.context = context
        super().__init__(self._format(message))

    def _format(self, message: str) -> str:
        if not self.context:
            return message
        details: list[str] = [f"sheet={self.context.sheet}"]
        if self.context.row_id is not None:
            details.append(f"row_id={self.context.row_id}")
        if self.context.column is not None:
            details.append(f"column={self.context.column}")
        if self.context.expected is not None:
            details.append(f"expected={self.context.expected}")
        if self.context.actual is not None:
            details.append(f"actual={self.context.actual}")
        return f"{message} ({', '.join(details)})"


class SheetAccessError(ExaspimProceduresError):
    """Raised when a Smartsheet cannot be accessed or fetched."""

    pass


class RowNotFoundError(ExaspimProceduresError):
    """Raised when an expected row is not found in a sheet."""

    pass


class DuplicateRowError(ExaspimProceduresError):
    """Raised when duplicate rows are found where only one is expected."""

    pass


class DataValidationError(ExaspimProceduresError):
    """Raised when data fails validation checks (missing, invalid, etc.)."""

    pass


class CrossSheetMismatchError(ExaspimProceduresError):
    """Raised when data across multiple sheets is inconsistent."""

    pass


class ChronologyError(ExaspimProceduresError):
    """Raised when procedure dates are out of expected chronological order."""

    pass
