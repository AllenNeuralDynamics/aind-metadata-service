from fastapi.responses import JSONResponse
from typing import Optional, List, Dict
from datetime import datetime
import json


def validate_parameters(date_performed: Optional[str], latest: bool):
    """Ensures that both `date_performed` and `latest` are not set simultaneously."""
    # TODO: should this return a JSONResponse or raise an error? Error should be in response?
    if date_performed and latest:
        raise Exception("Both date_performed and latest cannot be set.")
    return None  # No validation error


def parse_date_performed(date_performed: Optional[str]) -> Optional[datetime]:
    """Converts `date_performed` to a datetime object with zeroed seconds/microseconds."""
    if not date_performed:
        return None
    else:
        return datetime.fromisoformat(date_performed).replace(
            second=0, microsecond=0
        ) # if this raises an error -> it should throw internal server error
    # except ValueError:
    #     return JSONResponse(
    #         status_code=400,
    #         content={
    #             "message": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)",
    #             "data": None,
    #         },
    #     )

def filter_by_date(
    imaging_metadata: List[Dict], date_performed: datetime
) -> List[Dict]:
    """Filters imaging metadata by the given `date_performed`."""
    # TODO: no data found, or internal server error w message? 
    filtered_metadata = [
        data
        for data in imaging_metadata
        if data.get("date_performed")
        and datetime.fromisoformat(str(data["date_performed"])).replace(
            second=0, microsecond=0
        )
        == date_performed
    ]
    return filtered_metadata if filtered_metadata else []


def get_latest_metadata(imaging_metadata: List[Dict]) -> List[Dict]:
    """Finds the most recent imaging metadata based on `date_performed`."""
    #TODO: how to handle case where there is no date_performed in SLIMS? 
    # logging? 
    dated_metadata = [
        data for data in imaging_metadata if data.get("date_performed")
    ]
    print(dated_metadata[0]["date_performed"])
    return (
        [
            max(
                dated_metadata,
                key=lambda x: datetime.fromisoformat(str(x["date_performed"])),
            )
        ]
        if dated_metadata
        else []
    )


def format_response(imaging_metadata: List[Dict]) -> JSONResponse:
    """Formats the final JSON response based on the number of results."""
    if len(imaging_metadata) == 0:
        return JSONResponse(
            status_code=404,
            content={"message": "No Data Found.", "data": None},
        )
    else:
        return JSONResponse(
            status_code=200,
            content={
                "message": "Success",
                "data": json.loads(
                    json.dumps(imaging_metadata, default=str)
                ),
            },
        )
