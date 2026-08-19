"""Module to proxy requests v1 aind-metadata-service-server"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, Path, Query, Request, Response
from httpx import AsyncClient, RequestError
from starlette.datastructures import QueryParams

from aind_metadata_service_server.sessions import (
    get_aind_data_schema_v1_session,
)

router = APIRouter()


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


@router.get("/instrument/{instrument_id}")
async def get_v1_instrument(
    request: Request,
    instrument_id: str = Path(
        ...,
        openapi_examples={
            "default": {
                "summary": "A sample instrument ID",
                "description": "Example instrument ID",
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
