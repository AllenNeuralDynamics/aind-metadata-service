"""Base reader class for Smartsheet data extraction."""

from __future__ import annotations

import logging
from abc import ABC
from typing import Any

from exaspim_procedures_generation.exceptions import (
    DataValidationError,
    DuplicateRowError,
    ErrorContext,
    RowNotFoundError,
)
from exaspim_procedures_generation.smartsheet_client import SmartsheetClient

logger = logging.getLogger(__name__)


class BaseSheetReader(ABC):
    """Abstract base class for reading specimen data from a Smartsheet.

    Subclasses must define ``sheet_label``, ``required_columns``, and
    optionally override ``id_column``, ``required``, ``repeatable``,
    and ``contains_match``.

    Parameters
    ----------
    client : SmartsheetClient
        The Smartsheet API client.
    sheet_id : int
        The numeric Smartsheet sheet ID.
    specimen_id : str
        The specimen identifier to filter rows by.
    """

    # -- Subclass configuration --
    sheet_label: str = ""
    """Human-readable name for this sheet (used in error messages)."""

    required_columns: list[str] = []
    """Columns that must exist in the sheet for reading to proceed."""

    id_column: str = "Sample"
    """The column name used to match the specimen_id."""

    required: bool = True
    """If True, raises RowNotFoundError when no matching rows are found."""

    repeatable: bool = False
    """If True, allows multiple matching rows. If False, >1 row is an error."""

    contains_match: bool = False
    """If True, uses substring matching on the ID column."""

    def __init__(
        self,
        client: SmartsheetClient,
        sheet_id: int,
        specimen_id: str,
    ) -> None:
        self.client = client
        self.sheet_id = sheet_id
        self.specimen_id = specimen_id

    def build_filters(self) -> dict[str, Any]:
        """Build the filter dictionary for row lookup.

        Returns
        -------
        dict[str, Any]
            Filter criteria for find_rows.
        """
        return {self.id_column: self.specimen_id}

    def fetch_rows(self) -> list[dict[str, Any]]:
        """Fetch and validate rows from the sheet.

        Returns
        -------
        list[dict[str, Any]]
            List of matching row dictionaries.

        Raises
        ------
        RowNotFoundError
            If ``required=True`` and no matching rows found.
        DuplicateRowError
            If ``repeatable=False`` and more than one row matches.
        DataValidationError
            If required columns are missing or contain invalid values.
        """
        sheet = self.client.get_sheet(self.sheet_id)
        column_map = self.client.get_column_map(sheet)

        self._validate_columns(column_map)

        filters = self.build_filters()
        rows = self.client.find_rows(
            sheet, column_map, filters, contains_match=self.contains_match
        )

        self._validate_rows(rows)
        return rows

    def _validate_columns(self, column_map: dict[str, int]) -> None:
        """Verify that all required columns exist in the sheet.

        Parameters
        ----------
        column_map : dict[str, int]
            Available columns in the sheet.

        Raises
        ------
        DataValidationError
            If any required column is missing.
        """
        available = set(column_map.keys())
        missing = [col for col in self.required_columns if col not in available]
        if missing:
            raise DataValidationError(
                f"Missing required columns in {self.sheet_label}: {missing}",
                context=ErrorContext(
                    sheet=self.sheet_label,
                    expected=self.required_columns,
                    actual=list(available),
                ),
            )

    def _validate_rows(self, rows: list[dict[str, Any]]) -> None:
        """Validate the fetched rows for count and data quality.

        Parameters
        ----------
        rows : list[dict[str, Any]]
            The matched rows.

        Raises
        ------
        RowNotFoundError
            If required and no rows found.
        DuplicateRowError
            If not repeatable and more than one row found.
        DataValidationError
            If any required column contains '#INVALID VALUE'.
        """
        if not rows and self.required:
            raise RowNotFoundError(
                f"No matching row found for specimen '{self.specimen_id}' "
                f"in {self.sheet_label}.",
                context=ErrorContext(
                    sheet=self.sheet_label,
                    column=self.id_column,
                    expected=self.specimen_id,
                ),
            )

        if len(rows) > 1 and not self.repeatable:
            row_ids = [r.get("_row_id") for r in rows]
            raise DuplicateRowError(
                f"Found {len(rows)} rows for specimen '{self.specimen_id}' "
                f"in {self.sheet_label}, expected exactly 1.",
                context=ErrorContext(
                    sheet=self.sheet_label,
                    column=self.id_column,
                    expected="1 row",
                    actual=f"{len(rows)} rows (IDs: {row_ids})",
                ),
            )

        # Check for Smartsheet's #INVALID VALUE marker in required columns
        for row in rows:
            for col in self.required_columns:
                value = row.get(col)
                if isinstance(value, str) and "#INVALID VALUE" in value.upper():
                    raise DataValidationError(
                        f"Invalid value in column '{col}' of {self.sheet_label}.",
                        context=ErrorContext(
                            sheet=self.sheet_label,
                            row_id=row.get("_row_id"),
                            column=col,
                            actual=value,
                        ),
                    )
