"""Module to proxy requests v1 aind-metadata-service-server"""

from enum import Enum
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Path, Query, Request, Response
from httpx import AsyncClient, RequestError
from starlette.datastructures import QueryParams

from aind_metadata_service_server.sessions import (
    get_aind_data_schema_v1_session,
)

router = APIRouter()


class SlimsWorkflow(str, Enum):
    """Available workflows that can be queried."""

    SMARTSPIM_IMAGING = "smartspim_imaging"
    HISTOLOGY = "histology"
    WATER_RESTRICTION = "water_restriction"
    VIRAL_INJECTIONS = "viral_injections"
    ECEPHYS_SESSIONS = "ecephys_sessions"


async def proxy(
    request: Request,
    path: str,
    async_client: AsyncClient,
    query_params: QueryParams = QueryParams(),
) -> Response:
    """
    Proxy request to v1 aind-metadata-service-server
    Parameters
    ----------
    request : Request
    path : str
    async_client : AsyncClient
    query_params : QueryParams

    Returns
    -------
    Response

    """

    # Prepare headers to forward (excluding hop-by-hop headers)
    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower()
        not in [
            "host",
            "connection",
            "keep-alive",
            "proxy-authenticate",
            "proxy-authorization",
            "te",
            "trailers",
            "transfer-encoding",
            "upgrade",
        ]
    }

    try:
        backend_response = await async_client.request(
            method=request.method,
            url=path,
            headers=headers,
            params=query_params,
            timeout=240,  # Adjust timeout as needed
        )
        # Create a FastAPI Response from the backend's response
        response_headers = {
            key: value
            for key, value in backend_response.headers.items()
            if key.lower() not in ["content-encoding", "content-length"]
        }
        return Response(
            content=backend_response.content,
            status_code=backend_response.status_code,
            headers=response_headers,
            media_type=backend_response.headers.get("content-type"),
        )
    except RequestError as exc:
        return Response(f"Proxy request failed: {exc}", status_code=500)


@router.get("/funding/{project_name}")
async def get_v1_funding(
    request: Request,
    project_name: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample project name",
                "description": "Example project name for smartsheet",
                "value": (
                    "Discovery-Neuromodulator circuit dynamics during foraging"
                ),
            }
        },
    ),
    aind_data_schema_v1_session=Depends(get_aind_data_schema_v1_session),
):
    """
    Return funding metadata for a given project.
    """
    return await proxy(
        request, f"/funding/{project_name}", aind_data_schema_v1_session
    )


@router.get("/project_names")
async def get_v1_project_names(
    request: Request,
    aind_data_schema_v1_session=Depends(get_aind_data_schema_v1_session),
):
    """
    Get a list of project names from the Smartsheet API.
    """
    return await proxy(request, "/project_names", aind_data_schema_v1_session)


@router.get("/tars_injection_materials/{prep_lot_number}")
async def get_v1_injection_materials(
    request: Request,
    prep_lot_number: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample prep lot number",
                "description": "Example prep lot number for TARS",
                "value": "VT3214G",
            }
        },
    ),
    aind_data_schema_v1_session=Depends(get_aind_data_schema_v1_session),
):
    """
    ## Injection Materials V1
    Return Injection Materials metadata.
    """
    return await proxy(
        request,
        f"/tars_injection_materials/{prep_lot_number}",
        aind_data_schema_v1_session,
    )


@router.get("/intended_measurements/{subject_id}")
async def get_v1_intended_measurements(
    request: Request,
    subject_id: str = Path(
        ...,
        openapi_examples={
            "example1": {
                "summary": "A sample subject ID",
                "description": "Example subject ID for Procedures",
                "value": "775745",
            },
        },
    ),
    aind_data_schema_v1_session=Depends(get_aind_data_schema_v1_session),
):
    """
    ## Intended Measurements V1
    Return Intended Measurements metadata.
    """
    return await proxy(
        request,
        f"/intended_measurements/{subject_id}",
        aind_data_schema_v1_session,
    )


@router.get("/mgi_allele/{allele_name}")
async def get_v1_mgi_allele(
    request: Request,
    allele_name: str = Path(
        ...,
        openapi_examples={
            "cre_line": {
                "summary": "Cre line example",
                "description": "Example using a Cre recombinase line",
                "value": "Parvalbumin-IRES-Cre",
            },
            "gene_symbol": {
                "summary": "Gene symbol example",
                "description": "Example using a gene symbol",
                "value": "Pvalb",
            },
        },
    ),
    aind_data_schema_v1_session=Depends(get_aind_data_schema_v1_session),
):
    """
    ## MGI Allele
    Return MGI Allele metadata.
    """
    return await proxy(
        request, f"/mgi_allele/{allele_name}", aind_data_schema_v1_session
    )


@router.get("/perfusions/{subject_id}")
async def get_v1_perfusions(
    request: Request,
    subject_id: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample subject id",
                "description": "Example subject id",
                "value": "689418",
            }
        },
    ),
    aind_data_schema_v1_session=Depends(get_aind_data_schema_v1_session),
):
    """
    ## Perfusions V1
    Return Perfusions metadata.
    """
    return await proxy(
        request, f"/perfusions/{subject_id}", aind_data_schema_v1_session
    )


@router.get("/procedures/{subject_id}")
async def get_v1_procedures(
    request: Request,
    subject_id: str = Path(
        ...,
        openapi_examples={
            "example1": {
                "summary": "Subject ID Example 1",
                "description": "Example subject ID for Procedures",
                "value": "632269",
            },
            "example2": {
                "summary": "Subject ID Example 2",
                "description": "Example subject ID for Procedures",
                "value": "656374",
            },
            "example3": {
                "summary": "Subject ID Example 3",
                "description": "Example subject ID for Procedures",
                "value": "804998",
            },
        },
    ),
    aind_data_schema_v1_session=Depends(get_aind_data_schema_v1_session),
):
    """
    ## Procedures V1
    Return Procedure metadata.
    """
    return await proxy(
        request, f"/procedures/{subject_id}", aind_data_schema_v1_session
    )


@router.get("/protocols/{protocol_name}")
async def get_v1_protocols(
    request: Request,
    protocol_name: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample protocol name",
                "description": "Example protocol name",
                "value": (
                    "Tetrahydrofuran and Dichloromethane Delipidation of a "
                    "Whole Mouse Brain"
                ),
            }
        },
    ),
    aind_data_schema_v1_session=Depends(get_aind_data_schema_v1_session),
):
    """
    ## Protocols
    Return Protocols metadata.
    """
    return await proxy(
        request, f"/protocols/{protocol_name}", aind_data_schema_v1_session
    )


@router.get("/rig/{rig_id}")
async def get_v1_rig(
    request: Request,
    rig_id: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample rig ID",
                "description": "Example rig ID for SLIMS",
                "value": "323_EPHYS1_20250205",
            }
        },
    ),
    partial_match: bool = Query(False, alias="partial_match"),
    aind_data_schema_v1_session=Depends(get_aind_data_schema_v1_session),
):
    """
    ## Rig V1
    Return a Rig.
    """
    query_params = QueryParams({"partial_match": partial_match})
    return await proxy(
        request, f"/rig/{rig_id}", aind_data_schema_v1_session, query_params
    )


@router.get("/instrument/{instrument_id}")
async def get_v1_instrument(
    request: Request,
    instrument_id: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample instrument ID",
                "description": "Example instrument ID for SLIMS",
                "value": "440_SmartSPIM1_20240327",
            }
        },
    ),
    partial_match: bool = Query(False, alias="partial_match"),
    aind_data_schema_v1_session=Depends(get_aind_data_schema_v1_session),
):
    """
    ## Instrument v1
    Return an Instrument.
    """

    query_params = QueryParams({"partial_match": partial_match})
    return await proxy(
        request,
        f"/instrument/{instrument_id}",
        aind_data_schema_v1_session,
        query_params,
    )


@router.post("/bergamo_session")
async def get_v1_bergamo_session(
    request: Request,
    job_settings: Dict[str, Any],
    aind_data_schema_v1_session=Depends(get_aind_data_schema_v1_session),
):
    """
    ## Session
    Return session metadata computed from aind-metadata-mapper.
    """
    query_params = QueryParams(job_settings)
    return await proxy(
        request, "/bergamo_session", aind_data_schema_v1_session, query_params
    )


@router.get("/slims/{workflow}")
async def get_v1_slims_workflow(
    request: Request,
    workflow: SlimsWorkflow = Path(
        ...,
        description="The SLIMS workflow to query.",
    ),
    subject_id: Optional[str] = Query(
        None,
        alias="subject_id",
        description="Subject ID to filter the data.",
        openapi_examples={
            "smartspim_imaging_example": {
                "summary": "SmartSPIM example subject ID",
                "value": "744742",
            },
            "histology_example": {
                "summary": "Histology example subject ID",
                "value": "744742",
            },
            "water_restriction_example": {
                "summary": "Water restriction example subject ID",
                "value": "762287",
            },
            "viral_injections_example": {
                "summary": "Viral injections subject ID (None)",
                "value": None,
            },
            "ecephys_session_example": {
                "summary": "Ecephys example subject ID",
                "value": "750108",
            },
        },
    ),
    session_name: Optional[str] = Query(
        None,
        alias="session_name",
        description="Name of the session (only for ecephys sessions).",
        openapi_examples={
            "none_example": {
                "summary": "No session name (default)",
                "value": None,
            },
            "ecephys_session_example": {
                "summary": "Ecephys example session name",
                "value": "ecephys_750108_2024-12-23_14-51-45",
            },
        },
    ),
    start_date_gte: Optional[str] = Query(
        None,
        alias="start_date_gte",
        description="Experiment run created on or after. (ISO format)",
        openapi_examples={
            "smartspim_imaging_example": {
                "summary": "SmartSPIM example start date",
                "value": "2025-02-12",
            },
            "histology_example": {
                "summary": "Histology example start date",
                "value": "2025-02-06",
            },
            "water_restriction_example": {
                "summary": "Water restriction example start date",
                "value": "2024-12-13",
            },
            "viral_injections_example": {
                "summary": "Viral injections example start date",
                "value": "2025-04-22",
            },
            "ecephys_session_example": {
                "summary": "Ecephys example start date",
                "value": "2025-04-10",
            },
        },
    ),
    end_date_lte: Optional[str] = Query(
        None,
        alias="end_date_lte",
        description="Experiment run created on or before. (ISO format)",
        openapi_examples={
            "smartspim_imaging_example": {
                "summary": "SmartSPIM example end date",
                "value": "2025-02-13",
            },
            "histology_example": {
                "summary": "Histology example end date",
                "value": "2025-02-07",
            },
            "water_restriction_example": {
                "summary": "Water restriction example end date",
                "value": "2024-12-14",
            },
            "viral_injections_example": {
                "summary": "Viral injections example end date",
                "value": "2025-04-25",
            },
            "ecephys_session_example": {
                "summary": "Ecephys example end date",
                "value": "2025-04-11",
            },
        },
    ),
    aind_data_schema_v1_session=Depends(get_aind_data_schema_v1_session),
):
    """
    ## SLIMS V1
    Return information from SLIMS.
    """
    kwargs = {
        "subject_id": subject_id,
        "start_date_gte": start_date_gte,
        "end_date_lte": end_date_lte,
    }
    if workflow == SlimsWorkflow.ECEPHYS_SESSIONS:
        kwargs["session_name"] = session_name

    # Filter out None values to prevent them from being stringified
    filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
    query_params = QueryParams(filtered_kwargs)

    return await proxy(
        request,
        f"/slims/{workflow}",
        aind_data_schema_v1_session,
        query_params,
    )


@router.get("/subject/{subject_id}")
async def get_v1_subject(
    request: Request,
    subject_id: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample subject ID",
                "description": "Example subject ID for LabTracks",
                "value": "632269",
            }
        },
    ),
    aind_data_schema_v1_session=Depends(get_aind_data_schema_v1_session),
):
    """
    ## Subject V1
    Return Subject metadata.
    """
    return await proxy(
        request, f"/subject/{subject_id}", aind_data_schema_v1_session
    )
