"""Module to handle dataverse endpoints"""

from datetime import datetime, timedelta

from aind_dataverse_service_async_client.exceptions import ApiException
from fastapi import APIRouter, Depends, HTTPException, Path, Query

from aind_metadata_service_server.mappers.dataverse import (
    filter_dataverse_metadata,
)
from aind_metadata_service_server.sessions import get_dataverse_api_instance

router = APIRouter()


@router.get(
    "/api/v2/dataverse/tables",
    responses={
        404: {"description": "Not found"},
    },
)
async def get_dataverse_table_info(
    dataverse_api_instance=Depends(get_dataverse_api_instance),
):
    """
    ## Entity table identifying information
    Retrieves identifying information for all table entities in Dataverse.
    """
    dataverse_response = await dataverse_api_instance.get_table_info(
        _request_timeout=10
    )
    if not dataverse_response:
        raise HTTPException(status_code=404, detail="Not found")
    return dataverse_response


@router.get(
    "/api/v2/dataverse/tables/{entity_set_table_name}",
    responses={
        404: {"description": "Not found"},
    },
)
async def get_dataverse_table(
    entity_set_table_name: str = Path(
        ...,
        description="The entity set name of the table to fetch",
        openapi_examples={
            "default": {
                "summary": "A sample entity set name ID",
                "description": "Example entity set name",
                "value": "cr138_projects",
            }
        },
    ),
    columns: str | None = Query(
        default=None,
        description="Comma-separated column names to select from the table",
        openapi_examples={
            "default": {
                "summary": "A sample column selection",
                "description": "Example columns to select",
                "value": "modifiedon,statecode,cr138_projectname",
            }
        },
    ),
    filter: str | None = Query(
        default=None,
        description="OData-style filter expression",
        openapi_examples={
            "default": {
                "summary": "A sample filter expression",
                "description": "Example OData-style filter expression",
                "value": "cr138_projectname eq 'Barseq_GeneticTools'",
            }
        },
    ),
    dataverse_api_instance=Depends(get_dataverse_api_instance),
):
    """
    ## Table Data
    Retrieves data for a specific entity table in Dataverse.
    """
    try:

        dataverse_response = await dataverse_api_instance.get_table(
            entity_set_table_name,
            columns=columns,
            filter=filter,
            _request_timeout=10,
        )
        if not dataverse_response:
            raise HTTPException(status_code=404, detail="Not found")

        return filter_dataverse_metadata(dataverse_response)

    except ApiException as e:
        raise HTTPException(
            status_code=e.status,
            detail=f"Error fetching {entity_set_table_name}: {e.reason}",
        )

@router.get(
    "/api/v2/dataverse/mouse_weight_records/{subject_id}",
    responses={
        404: {"description": "Not found"},
    }
)
async def get_mouse_weight_records(
        subject_id: str = Path(
            ...,
            description="The subject ID to fetch mouse weight records for",
            openapi_examples={
                "default": {
                    "summary": "A sample subject ID",
                    "description": "Example subject ID",
                    "value": "865390",
                }
            },
        ),
        acquisition_datetime: str | datetime | None = Query(
            default=None,
            description="Filter records by acquisition datetime (ISO format string or datetime object)",
            openapi_examples={
                "default": {
                    "summary": "A sample acquisition datetime",
                    "description": "Example acquisition datetime",
                    "value": "2026-08-06T00:18:00",
                }
            },
        ),
    dataverse_api_instance=Depends(get_dataverse_api_instance),
):
    """
    ## Mouse Weight Records
    Retrieves mouse weight records from Dataverse.
    """
    filter_query = f"aibs_mouse_id/aibs_mouse_id eq '{subject_id}'"
    if acquisition_datetime:
        # Handle both string and datetime types
        if isinstance(acquisition_datetime, str):
            dt_str = acquisition_datetime if acquisition_datetime.endswith('Z') else f"{acquisition_datetime}Z"
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        else:
            # Already a datetime object
            dt = acquisition_datetime
        # Get start and end of the day
        start_of_day = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        start_str = start_of_day.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_str = end_of_day.strftime("%Y-%m-%dT%H:%M:%SZ")
        filter_query += f" and cr138_datetime ge {start_str} and cr138_datetime lt {end_str}"
    try:
        dataverse_response = await dataverse_api_instance.get_table(
            entity_set_table_name="aibs_fact_mouse_weight_recordses",
            filter=filter_query,
            _request_timeout=10,
        )
        if not dataverse_response:
            raise HTTPException(status_code=404, detail="Not found")
        return filter_dataverse_metadata(dataverse_response)

    except ApiException as e:
        raise HTTPException(
            status_code=e.status,
            detail=f"Error fetching mouse weight records: {e.reason}",
        )
