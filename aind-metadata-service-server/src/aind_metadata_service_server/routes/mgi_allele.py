"""Module to handle allele endpoints"""

from fastapi import APIRouter, Depends, Path

from aind_metadata_service_server.mappers.mgi_allele import MgiMapper
from aind_metadata_service_server.response_handler import (
    ModelResponse,
    StatusCodes,
)
from aind_metadata_service_server.sessions import get_mgi_api_instance

router = APIRouter()


@router.get("/mgi_allele/{allele_name}")
async def get_mgi_allele(
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
    mgi_api_instance=Depends(get_mgi_api_instance),
):
    """
    ## MGI Allele
    Return MGI Allele metadata.
    """
    mgi_response = await mgi_api_instance.get_allele_info(
        allele_name=allele_name, _request_timeout=10
    )
    mappers = [
        MgiMapper(mgi_summary_row=mgi_summary_row)
        for mgi_summary_row in mgi_response
    ]
    pid_models = [
        mapper.map_to_aind_pid_name()
        for mapper in mappers
        if mapper.map_to_aind_pid_name()
    ]
    response_handler = ModelResponse(
        aind_models=pid_models, status_code=StatusCodes.DB_RESPONDED
    )
    response = response_handler.map_to_json_response()
    return response
