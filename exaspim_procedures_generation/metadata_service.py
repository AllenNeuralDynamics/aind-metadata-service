"""Integration with the AIND metadata-service for perfusion data."""

from __future__ import annotations

import logging
from datetime import date
from typing import Any

import requests

from exaspim_procedures_generation.exceptions import (
    CrossSheetMismatchError,
    DataValidationError,
    ErrorContext,
)

logger = logging.getLogger(__name__)

# Default metadata-service base URL
METADATA_SERVICE_URL = "http://aind-metadata-service"


def fetch_subject_procedures(
    specimen_id: str,
    base_url: str = METADATA_SERVICE_URL,
) -> dict[str, Any] | None:
    """Fetch the procedures record for a subject from the metadata-service.

    Parameters
    ----------
    specimen_id : str
        The subject/specimen ID to query.
    base_url : str
        Base URL of the AIND metadata-service.

    Returns
    -------
    dict[str, Any] | None
        The procedures JSON dict, or None if unavailable.
    """
    url = f"{base_url}/subject_procedures/{specimen_id}"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.json()
        logger.warning(
            "Metadata-service returned status %d for %s",
            response.status_code,
            specimen_id,
        )
        return None
    except requests.RequestException as e:
        logger.warning(
            "Failed to reach metadata-service for %s: %s", specimen_id, e
        )
        return None


def extract_perfusion_surgery(
    procedures_data: dict[str, Any],
) -> dict[str, Any] | None:
    """Extract the perfusion Surgery object from a procedures record.

    Parameters
    ----------
    procedures_data : dict[str, Any]
        The full procedures JSON from metadata-service.

    Returns
    -------
    dict[str, Any] | None
        The perfusion Surgery dict, or None if not found.
    """
    subject_procedures = procedures_data.get("subject_procedures", [])
    for proc in subject_procedures:
        # Look for a Surgery that contains a Perfusion procedure
        procedures_list = proc.get("procedures", [])
        for sub_proc in procedures_list:
            proc_type = sub_proc.get("procedure_type", "")
            if "perfusion" in proc_type.lower():
                return proc
    return None


def fetch_perfusion_date_from_service(
    specimen_id: str,
    base_url: str = METADATA_SERVICE_URL,
) -> date | None:
    """Fetch just the perfusion date from the metadata-service.

    Parameters
    ----------
    specimen_id : str
        The subject/specimen ID.
    base_url : str
        Base URL of the AIND metadata-service.

    Returns
    -------
    date | None
        The perfusion date, or None if unavailable.
    """
    procedures_data = fetch_subject_procedures(specimen_id, base_url)
    if procedures_data is None:
        return None

    surgery = extract_perfusion_surgery(procedures_data)
    if surgery is None:
        return None

    raw_date = surgery.get("start_date")
    if raw_date is None:
        return None

    from datetime import datetime

    try:
        return datetime.strptime(str(raw_date), "%Y-%m-%d").date()
    except ValueError:
        logger.warning("Could not parse perfusion date from service: %s", raw_date)
        return None


def compare_perfusion_dates(
    specimen_id: str,
    smartsheet_date: date,
    base_url: str = METADATA_SERVICE_URL,
) -> date:
    """Cross-validate the perfusion date between Smartsheet and metadata-service.

    Parameters
    ----------
    specimen_id : str
        The subject/specimen ID.
    smartsheet_date : date
        The perfusion date from the Smartsheet.
    base_url : str
        Base URL of the AIND metadata-service.

    Returns
    -------
    date
        The validated perfusion date.

    Raises
    ------
    CrossSheetMismatchError
        If the dates disagree between sources.
    """
    service_date = fetch_perfusion_date_from_service(specimen_id, base_url)

    if service_date is None:
        logger.info(
            "Metadata-service perfusion date not available for %s; "
            "using Smartsheet date %s.",
            specimen_id,
            smartsheet_date,
        )
        return smartsheet_date

    if service_date != smartsheet_date:
        raise CrossSheetMismatchError(
            f"Perfusion date mismatch for {specimen_id}: "
            f"metadata-service={service_date}, Smartsheet={smartsheet_date}.",
            context=ErrorContext(
                sheet="metadata-service",
                column="Perfusion Date",
                expected=service_date.isoformat(),
                actual=smartsheet_date.isoformat(),
            ),
        )

    logger.info("Perfusion date validated: %s", service_date)
    return service_date
