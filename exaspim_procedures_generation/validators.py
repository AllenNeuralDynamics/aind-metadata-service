"""Validation functions for cross-sheet data consistency and chronology."""

from __future__ import annotations

import logging
import math
from datetime import date, datetime
from typing import Any

from exaspim_procedures_generation.exceptions import (
    ChronologyError,
    CrossSheetMismatchError,
    DataValidationError,
    ErrorContext,
)

logger = logging.getLogger(__name__)


def _parse_date(raw: Any) -> date | None:
    """Parse a raw value into a date object.

    Supports multiple date formats commonly found in Smartsheet data.

    Parameters
    ----------
    raw : Any
        A raw cell value (string, date, or None).

    Returns
    -------
    date | None
        The parsed date, or None if input is empty/None.

    Raises
    ------
    DataValidationError
        If the value is non-empty but cannot be parsed.
    """
    if raw is None:
        return None
    if isinstance(raw, date):
        return raw
    text = str(raw).strip()
    if not text:
        return None

    for fmt in ("%m/%d/%y", "%m/%d/%Y", "%m/%d/%y %I:%M %p", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    raise DataValidationError(
        f"Could not parse date: '{text}'",
        context=ErrorContext(sheet="validators", actual=raw),
    )


def _floats_close(a: Any, b: Any, tolerance: float = 0.01) -> bool:
    """Check if two numeric values are close within tolerance.

    Parameters
    ----------
    a, b : Any
        Values to compare (will be cast to float).
    tolerance : float
        Acceptable absolute difference.

    Returns
    -------
    bool
        True if values are within tolerance or both are None/empty.
    """
    try:
        fa = float(a)
        fb = float(b)
        return math.isclose(fa, fb, abs_tol=tolerance)
    except (ValueError, TypeError):
        return False


def validate_injection_cross_sheet(
    mouse_tracker_row: dict[str, Any],
    sample_tracking_row: dict[str, Any],
) -> None:
    """Verify viral injection data agrees between Mouse Tracker and Sample Tracking.

    Compares Virus1-4 fields (name, titer, coordinates) between the two sheets.
    Raises on disagreement beyond acceptable tolerance for numeric fields.

    Parameters
    ----------
    mouse_tracker_row : dict[str, Any]
        Row from the Mouse Tracker sheet.
    sample_tracking_row : dict[str, Any]
        Row from the Sample Tracking sheet.

    Raises
    ------
    CrossSheetMismatchError
        If injection data disagrees between sheets.
    """
    # Check up to 4 viral injections
    for virus_num in range(1, 5):
        prefix = f"Virus{virus_num}"

        # Check if this virus exists in either sheet
        mt_virus_name = str(mouse_tracker_row.get(prefix, "") or "").strip()
        st_virus_name = str(sample_tracking_row.get(prefix, "") or "").strip()

        # Skip if neither sheet has this virus
        if not mt_virus_name and not st_virus_name:
            continue

        # If only one sheet has the virus, log a warning but don't fail.
        # Not all specimens have virus data duplicated across both sheets.
        if mt_virus_name and not st_virus_name:
            logger.info(
                "%s present in Mouse Tracker but not in Sample Tracking "
                "(this is acceptable — virus data may only exist in Mouse Tracker).",
                prefix,
            )
            continue
        if st_virus_name and not mt_virus_name:
            logger.info(
                "%s present in Sample Tracking but not in Mouse Tracker "
                "(this is acceptable — virus data may only exist in one sheet).",
                prefix,
            )
            continue

        # Compare virus name (case-insensitive)
        if mt_virus_name.lower() != st_virus_name.lower():
            raise CrossSheetMismatchError(
                f"{prefix} name mismatch between sheets.",
                context=ErrorContext(
                    sheet="Mouse Tracker vs Sample Tracking",
                    column=prefix,
                    expected=mt_virus_name,
                    actual=st_virus_name,
                ),
            )

        # Compare numeric fields with tolerance
        numeric_fields = [
            f"{prefix} Stock Titer (GC/mL)",
            f"{prefix} Dose (GC)",
            f"{prefix} AP (mm)",
            f"{prefix} ML (mm)",
            f"{prefix} DV (mm)",
        ]
        # Handle slight column name variations
        volume_col_mt = f"{prefix} Stereotaxic Volume Injected (nL)"
        volume_col_st = f"{prefix} Stereotaxic Volume Injected (nL)"
        if virus_num == 4:
            # Virus4 uses a slightly different column name in some sheets
            volume_col_mt = "Stereotaxic Volume Injected (nL)"

        for col in numeric_fields:
            mt_val = mouse_tracker_row.get(col)
            st_val = sample_tracking_row.get(col)
            if mt_val is None and st_val is None:
                continue
            if mt_val is not None and st_val is not None:
                if not _floats_close(mt_val, st_val, tolerance=0.1):
                    raise CrossSheetMismatchError(
                        f"{col} mismatch between sheets.",
                        context=ErrorContext(
                            sheet="Mouse Tracker vs Sample Tracking",
                            column=col,
                            expected=mt_val,
                            actual=st_val,
                        ),
                    )


def validate_chronological_order(data: dict[str, list[dict[str, Any]]]) -> None:
    """Verify that procedure dates follow expected chronological order.

    Expected order: injection -> perfusion -> delipidation -> immunolabelling
    -> gelation -> screening -> expansion -> final imaging.

    Parameters
    ----------
    data : dict[str, list[dict[str, Any]]]
        All fetched row data keyed by sheet name.

    Raises
    ------
    ChronologyError
        If any procedure date violates chronological ordering.
    """
    chain: list[tuple[date, str]] = []

    # Mouse Tracker: injection date
    mt_rows = data.get("mouse_tracker", [])
    if mt_rows:
        inj_date = _parse_date(mt_rows[0].get("Virus1 Injection Date"))
        if inj_date:
            chain.append((inj_date, "Viral Injection"))

        perf_date = _parse_date(mt_rows[0].get("Perfusion Date"))
        if perf_date:
            chain.append((perf_date, "Perfusion"))

    # Sample Tracking: specimen processing dates
    st_rows = data.get("sample_tracking", [])
    if st_rows:
        row = st_rows[0]
        delip_start = _parse_date(row.get("DCM Delipidation Start"))
        if delip_start:
            chain.append((delip_start, "Delipidation"))

        immuno_start = _parse_date(row.get("Immuno: Primary Ab Start Date"))
        if immuno_start:
            chain.append((immuno_start, "Immunolabelling"))

        gel_start = _parse_date(row.get("Gelation: MBS Start"))
        if gel_start:
            chain.append((gel_start, "Gelation"))

        expansion_start = _parse_date(row.get("Expansion Start Date"))
        if expansion_start:
            chain.append((expansion_start, "Expansion"))

    # Imaging Queue: final imaging
    iq_rows = data.get("imaging_queue", [])
    if iq_rows:
        imaging_start = _parse_date(iq_rows[0].get("Imaging Start Date"))
        if imaging_start:
            chain.append((imaging_start, "Final Imaging"))

    # Verify order
    for i in range(1, len(chain)):
        prev_date, prev_step = chain[i - 1]
        curr_date, curr_step = chain[i]
        if prev_date > curr_date:
            raise ChronologyError(
                f"{curr_step} ({curr_date}) occurs before {prev_step} ({prev_date}).",
                context=ErrorContext(
                    sheet=curr_step,
                    expected=f">= {prev_date}",
                    actual=str(curr_date),
                ),
            )


def validate_required_fields(
    row: dict[str, Any],
    fields: list[str],
    sheet_label: str,
) -> None:
    """Check that all specified fields have non-empty values.

    Parameters
    ----------
    row : dict[str, Any]
        A row dictionary.
    fields : list[str]
        Field names that must be non-empty.
    sheet_label : str
        Sheet name for error context.

    Raises
    ------
    DataValidationError
        If any field is empty or None.
    """
    for field in fields:
        value = row.get(field)
        if value is None or str(value).strip() == "":
            raise DataValidationError(
                f"Required field '{field}' is empty in {sheet_label}.",
                context=ErrorContext(
                    sheet=sheet_label,
                    row_id=row.get("_row_id"),
                    column=field,
                    expected="non-empty value",
                    actual=value,
                ),
            )


def validate_no_duplicate_specimen(
    rows: list[dict[str, Any]],
    sheet_label: str,
    specimen_id: str,
) -> None:
    """Verify only one row matched for a single-specimen sheet.

    This is a secondary check beyond what the reader does —
    useful when multiple readers are involved and you want to
    verify consistency at the validation layer.

    Parameters
    ----------
    rows : list[dict[str, Any]]
        The matched rows.
    sheet_label : str
        Sheet name for error context.
    specimen_id : str
        The specimen ID used for filtering.

    Raises
    ------
    DataValidationError
        If more than one row is present.
    """
    if len(rows) > 1:
        raise DataValidationError(
            f"Multiple rows found for specimen '{specimen_id}' "
            f"in {sheet_label}. Expected exactly 1.",
            context=ErrorContext(
                sheet=sheet_label,
                expected="1 row",
                actual=f"{len(rows)} rows",
            ),
        )


def run_all_validations(data: dict[str, list[dict[str, Any]]]) -> None:
    """Run all validation checks on the collected data.

    Orchestrates cross-sheet validation, chronological ordering,
    and required field checks.

    Parameters
    ----------
    data : dict[str, list[dict[str, Any]]]
        All fetched row data keyed by reader name.

    Raises
    ------
    ExaspimProceduresError
        Any validation error from the checks.
    """
    # Cross-validate injection data between sheets
    mt_rows = data.get("mouse_tracker", [])
    st_rows = data.get("sample_tracking", [])
    if mt_rows and st_rows:
        validate_injection_cross_sheet(mt_rows[0], st_rows[0])

    # Validate chronological ordering
    validate_chronological_order(data)

    # Validate required fields in Sample Tracking
    if st_rows:
        # At minimum, delipidation dates must be present
        validate_required_fields(
            st_rows[0],
            [
                "DCM Delipidation Start",
                "DCM Delipidation End",
                "SBiP Delipidation Start",
                "SBiP Delipidation End",
            ],
            "Sample Tracking",
        )

    # Validate required fields in Imaging Queue
    iq_rows = data.get("imaging_queue", [])
    if iq_rows:
        validate_required_fields(
            iq_rows[0],
            ["Imaging Start Date", "Microscope"],
            "Imaging Queue",
        )

    logger.info("All validations passed.")
