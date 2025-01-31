from fastapi.responses import JSONResponse
from typing import Optional, List, Dict
from datetime import datetime


def validate_parameters(
    date_performed: Optional[str], latest: bool
) -> Optional[JSONResponse]:
    """Ensures that both `date_performed` and `latest` are not set simultaneously."""
    if date_performed and latest:
        return JSONResponse(
            status_code=400,
            content={
                "message": "Cannot provide both date_performed and latest parameters",
                "data": None,
            },
        )
    return None  # No validation error


def parse_date_performed(date_performed: Optional[str]) -> Optional[datetime]:
    """Converts `date_performed` to a datetime object with zeroed seconds/microseconds."""
    if not date_performed:
        return None
    try:
        return datetime.fromisoformat(date_performed).replace(
            second=0, microsecond=0
        )
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={
                "message": "Invalid date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)",
                "data": None,
            },
        )


def filter_by_date(
    imaging_metadata: List[Dict], date_performed: datetime
) -> List[Dict]:
    """Filters imaging metadata by the given `date_performed`."""
    filtered_metadata = [
        data
        for data in imaging_metadata
        if data.get("date_performed")
        and datetime.fromisoformat(data["date_performed"]).replace(
            second=0, microsecond=0
        )
        == date_performed
    ]
    return filtered_metadata if filtered_metadata else imaging_metadata


def get_latest_metadata(imaging_metadata: List[Dict]) -> List[Dict]:
    """Finds the most recent imaging metadata based on `date_performed`."""
    dated_metadata = [
        data for data in imaging_metadata if "date_performed" in data
    ]
    return (
        [
            max(
                dated_metadata,
                key=lambda x: datetime.fromisoformat(x["date_performed"]),
            )
        ]
        if dated_metadata
        else imaging_metadata
    )


def format_response(imaging_metadata: List[Dict]) -> JSONResponse:
    """Formats the final JSON response based on the number of results."""
    if len(imaging_metadata) > 1:
        return JSONResponse(
            status_code=300,
            content={
                "message": "Multiple Items Found.",
                "data": imaging_metadata,
            },
        )
    return JSONResponse(
        status_code=200,
        content={"message": "Success", "data": imaging_metadata[0]},
    )
