"""Module to handle dataverse data mapping and filtering"""

from typing import Dict, List
from fastapi import HTTPException


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


def apply_query_parameters(
    data: List[Dict], query_params: Dict[str, str]
) -> List[Dict]:
    """
    Apply query parameter filters to a list of records.

    Parameters
    ----------
    data : List[Dict]
        List of records to filter
    query_params : Dict[str, str]
        Dictionary of query parameter names and values to filter by

    Returns
    -------
    List[Dict]
        Filtered list of records. Returns empty list if query parameters 
        don't match any columns in the table.
    """
    if not query_params or not data:
        return data

    available_columns = set(data[0].keys())
    for param_key in query_params.keys():
        if param_key not in available_columns:
            return []

    filtered_records = []
    for record in data:
        match = True
        for param_key, param_value in query_params.items():
            record_value = str(record.get(param_key, "")).lower()
            param_value_lower = str(param_value).lower()
            if record_value != param_value_lower:
                match = False
                break
        if match:
            filtered_records.append(record)

    return filtered_records
