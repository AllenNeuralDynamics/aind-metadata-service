"""Module to handle allele endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Path

from aind_metadata_service_server.mappers.mgi_allele import MgiMapper
from aind_metadata_service_server.mappers.responses import map_to_response
from aind_metadata_service_server.sessions import get_mgi_api_instance

router = APIRouter()


@router.get(
    "/api/v2/mgi_allele/{allele_name}",
    responses={
        400: {
            "description": "Validation error in response model.",
            "headers": {
                "X-Error-Message": {
                    "description": "A JSON-encoded list of Pydantic validation errors.",
                    "schema": {
                        "type": "string"
                    }
                }
            }
        },
        404: {"description": "Not found"},
    },
)
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
    if len(pid_models) == 0:
        raise HTTPException(status_code=404, detail="Not found")
    else:
        return map_to_response(pid_models)
