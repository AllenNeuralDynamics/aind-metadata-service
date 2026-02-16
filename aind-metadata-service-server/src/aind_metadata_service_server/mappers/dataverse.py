"""Module to handle dataverse data mapping and filtering"""

from typing import Dict


def _filter_dataverse_metadata(data: Dict) -> Dict:
    """
    Filter out Dataverse metadata fields from the response.
    Parameters
    ----------
    data : Dict
        The dataverse response data (can be dict, list, or other)
    
    Returns
    -------
    Dict
        Filtered data with metadata fields removed
    """
    if isinstance(data, dict):
        return {
            key: _filter_dataverse_metadata(value)
            for key, value in data.items()
            if not (key.startswith("@") or "@" in key or key.startswith("_"))
        }
    elif isinstance(data, list):
        return [_filter_dataverse_metadata(item) for item in data]
    else:
        return data
