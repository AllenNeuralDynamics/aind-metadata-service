"""Module to handle dataverse data mapping and filtering"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from aind_metadata_service_server.models import MouseWeightData

logger = logging.getLogger(__name__)


def filter_dataverse_metadata(data: Dict) -> Dict:
    """
    Filter out Dataverse metadata fields from the response.
    Parameters
    ----------
    data : Dict
        The dataverse response data

    Returns
    -------
    Dict
        Filtered data with metadata fields removed
    """
    if isinstance(data, dict):
        return {
            key: filter_dataverse_metadata(value)
            for key, value in data.items()
            if (
                key.endswith("@OData.Community.Display.V1.FormattedValue")
                or not (
                    key.startswith("@") or "@" in key or key.startswith("_")
                )
            )
        }
    elif isinstance(data, list):
        return [filter_dataverse_metadata(item) for item in data]
    else:
        return data


def map_mouse_weight_records(
    dataverse_response: List[Dict],
) -> List[MouseWeightData]:
    """
    Map Dataverse mouse weight records to MouseWeightData models.

    Parameters
    ----------
    dataverse_response : List[Dict]
        The raw Dataverse API response as a list of records

    Returns
    -------
    List[MouseWeightData]
        List of mapped MouseWeightData models
    """
    if not dataverse_response:
        return []

    mapped_records = []

    for i, record in enumerate(dataverse_response):
        mapped_record = MouseWeightData(
            record_id=record.get("aibs_fact_mouse_weight_recordsid"),
            mouse_id=record.get(
                "_aibs_mouse_id_value@OData.Community.Display.V1."
                "FormattedValue"
            ),
            weight=record.get("aibs_weight"),
            weight_datetime=_parse_datetime(
                record.get("cr138_datetime")
            ),
            is_baseline_weight=record.get("aibs_is_baseline_weight"),
            operator=record.get(
                "_aibs_operator_value@OData.Community.Display.V1."
                "FormattedValue"
            ),
            workstation=record.get("aibs_workstation"),
            software_version=record.get("aibs_software_version"),
            software_source=record.get("aibs_software_source"),
            status=record.get(
                "statuscode@OData.Community.Display.V1.FormattedValue"
            ),
            notes=record.get("aibs_notes"),
        )
        mapped_records.append(mapped_record)
    return mapped_records


def _parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """
    Parse ISO datetime string to datetime object.

    Parameters
    ----------
    dt_str : Optional[str]
        ISO format datetime string

    Returns
    -------
    Optional[datetime]
        Parsed datetime object or None
    """
    if dt_str is None:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None
