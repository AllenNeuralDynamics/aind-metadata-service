"""Module to handle dataverse data mapping and filtering"""

from typing import Dict
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


def apply_query_parameters(data, query_params: Dict[str, str]):
    """
    Apply query parameter filters to dataverse table data.

    Parameters
    ----------
    data : Dict or List
        The dataverse response data
    query_params : Dict[str, str]
        Dictionary of query parameter names and values to filter by

    Returns
    -------
    Dict or List
        Filtered data with matching records (same structure as input)

    Raises
    ------
    HTTPException
        If query parameter doesn't match any column in the table
    """
    if not query_params:
        return data

    # Handle different data structures
    if isinstance(data, dict):
        if "value" not in data:
            return data
        records = data.get("value", [])
    elif isinstance(data, list):
        records = data
    else:
        return data

    if not records:
        return data

    # Check if query parameters exist in the table columns
    if records:
        available_columns = set(records[0].keys())
        for param_key in query_params.keys():
            if param_key not in available_columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"Query parameter '{param_key}' does not match any "
                    f"column in the table. Available columns: "
                    f"{', '.join(sorted(available_columns))}",
                )

    # Apply query parameter filters
    filtered_records = []
    for record in records:
        match = True
        for param_key, param_value in query_params.items():
            # Convert both values to string for comparison (case-insensitive)
            record_value = str(record.get(param_key, "")).lower()
            param_value_lower = str(param_value).lower()
            if record_value != param_value_lower:
                match = False
                break
        if match:
            filtered_records.append(record)

    # Return the same structure as input
    if isinstance(data, dict):
        result = data.copy()
        result["value"] = filtered_records
        return result
    else:
        return filtered_records
