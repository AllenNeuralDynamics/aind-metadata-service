"""Utility methods for handling smartspim imaging."""

from typing import Optional, List
from datetime import datetime, timezone
import logging
from aind_metadata_service.models import SpimImagingInformation


def parse_date_performed(date_performed: Optional[str]) -> Optional[datetime]:
    """
    Converts `date_performed` to a datetime object with zeroed
    seconds/microseconds.
    """
    if not date_performed:
        return None
    else:
        try:
            return datetime.fromisoformat(date_performed).replace(
                second=0, microsecond=0
            )
        except ValueError as e:
            logging.error(repr(e))
            return None


def filter_by_date(
    imaging_metadata: List[SpimImagingInformation], date_performed: datetime
) -> Optional[List[SpimImagingInformation]]:
    """
    Filters imaging metadata by the given `date_performed`.
    If no data is found, returns an empty list.
    """
    if date_performed.tzinfo is None:
        date_performed = date_performed.replace(tzinfo=timezone.utc)
    filtered_metadata = [
        data
        for data in imaging_metadata
        if getattr(data, "date_performed", None)
        and data.date_performed.replace(second=0, microsecond=0)
        == date_performed
    ]
    return filtered_metadata if filtered_metadata else []


def get_latest_metadata(
    imaging_metadata: List[SpimImagingInformation],
) -> Optional[List[SpimImagingInformation]]:
    """
    Finds the most recent imaging metadata based on `date_performed`.
    If no data is found, returns an empty list.
    """
    dated_metadata = [
        data
        for data in imaging_metadata
        if getattr(data, "date_performed", None)
    ]
    return (
        [max(dated_metadata, key=lambda x: x.date_performed)]
        if dated_metadata
        else []
    )
