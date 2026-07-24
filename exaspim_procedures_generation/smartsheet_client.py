"""Thin wrapper around the Smartsheet Python SDK for ExaSPIM pipeline use."""

from __future__ import annotations

import logging
from typing import Any

import smartsheet  # type: ignore[import-untyped]

from exaspim_procedures_generation.exceptions import (
    ErrorContext,
    SheetAccessError,
)

logger = logging.getLogger(__name__)


class SmartsheetClient:
    """Client for reading data from Smartsheet sheets.

    Wraps the ``smartsheet-python-sdk`` to provide a simplified interface
    for fetching sheets, extracting column maps, and finding rows by filter
    criteria.

    Parameters
    ----------
    access_token : str
        Smartsheet API access token.
    """

    def __init__(self, access_token: str) -> None:
        self._client = smartsheet.Smartsheet(access_token=access_token)
        self._client.errors_as_exceptions(True)

    def get_sheet(self, sheet_id: int) -> Any:
        """Fetch a full sheet by its numeric ID.

        Parameters
        ----------
        sheet_id : int
            The Smartsheet sheet ID.

        Returns
        -------
        smartsheet.models.Sheet
            The fetched sheet object.

        Raises
        ------
        SheetAccessError
            If the sheet cannot be accessed.
        """
        try:
            return self._client.Sheets.get_sheet(sheet_id)
        except Exception as e:
            raise SheetAccessError(
                f"Failed to access sheet {sheet_id}: {e}",
                context=ErrorContext(sheet=str(sheet_id)),
            ) from e

    def get_column_map(self, sheet: Any) -> dict[str, int]:
        """Build a mapping from column title to column ID.

        Parameters
        ----------
        sheet : smartsheet.models.Sheet
            A fetched sheet object.

        Returns
        -------
        dict[str, int]
            Mapping of column_title -> column_id.
        """
        return {col.title: col.id for col in sheet.columns}

    def get_cell_value(self, row: Any, column_id: int) -> Any:
        """Extract the display or actual value of a cell.

        Parameters
        ----------
        row : smartsheet.models.Row
            A row from a sheet.
        column_id : int
            The column ID to look up.

        Returns
        -------
        Any
            The cell's display_value (preferred) or value, or None.
        """
        for cell in row.cells:
            if cell.column_id == column_id:
                return cell.display_value if cell.display_value else cell.value
        return None

    def row_to_dict(self, row: Any, column_map: dict[str, int]) -> dict[str, Any]:
        """Convert a row to a dictionary keyed by column title.

        Parameters
        ----------
        row : smartsheet.models.Row
            A row from a sheet.
        column_map : dict[str, int]
            Column title to column ID mapping.

        Returns
        -------
        dict[str, Any]
            Row data as {column_title: cell_value}.
        """
        result: dict[str, Any] = {"_row_id": row.id}
        for title, col_id in column_map.items():
            result[title] = self.get_cell_value(row, col_id)
        return result

    def find_rows(
        self,
        sheet: Any,
        column_map: dict[str, int],
        filters: dict[str, Any],
        contains_match: bool = False,
    ) -> list[dict[str, Any]]:
        """Find rows matching all filter criteria.

        Parameters
        ----------
        sheet : smartsheet.models.Sheet
            A fetched sheet object.
        column_map : dict[str, int]
            Column title to column ID mapping.
        filters : dict[str, Any]
            Filter criteria as {column_title: expected_value}.
            Values are compared case-insensitively with whitespace stripped.
        contains_match : bool
            If True, uses substring matching (the cell value contains the
            filter value). Useful for columns with annotations (e.g.,
            Mouse Tracker "Mouse ID" has cre-line info appended).

        Returns
        -------
        list[dict[str, Any]]
            List of matching rows as dictionaries.
        """
        matching_rows: list[dict[str, Any]] = []

        for row in sheet.rows:
            if self._matches_filters(
                row, column_map, filters, contains_match=contains_match
            ):
                matching_rows.append(self.row_to_dict(row, column_map))

        return matching_rows

    def _matches_filters(
        self,
        row: Any,
        column_map: dict[str, int],
        filters: dict[str, Any],
        contains_match: bool = False,
    ) -> bool:
        """Check if a row matches all filter criteria.

        Parameters
        ----------
        row : smartsheet.models.Row
            The row to check.
        column_map : dict[str, int]
            Column title to column ID mapping.
        filters : dict[str, Any]
            Filter criteria.
        contains_match : bool
            Whether to use substring matching.

        Returns
        -------
        bool
            True if the row matches all filters.
        """
        for col_title, expected in filters.items():
            col_id = column_map.get(col_title)
            if col_id is None:
                return False

            cell_value = self.get_cell_value(row, col_id)
            if cell_value is None:
                return False

            cell_str = str(cell_value).strip().lower()
            expected_str = str(expected).strip().lower()

            if contains_match:
                if expected_str not in cell_str:
                    return False
            else:
                if cell_str != expected_str:
                    return False

        return True
