"""Module for the main index route"""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from aind_metadata_service_server import __version__ as service_version

router = APIRouter()

template_directory = str(
    (Path(__file__).parent.parent / "templates").resolve()
)
templates = Jinja2Templates(directory=template_directory)


@router.get("/")
async def index(request: Request):
    """
    Returns the index page with search UIs for enabled endpoints.
    """
    return templates.TemplateResponse(
        name="index.html",
        context=(
            {
                "request": request,
                "service_name": "AIND Metadata Service",
                "service_description": (
                    "REST service to retrieve metadata from AIND databases."
                ),
                "service_version": service_version,
                "endpoints": [
                    {
                        "endpoint": "subject",
                        "description": (
                            "Retrieve subject metadata from Labtracks server"
                        ),
                        "parameter": "subject_id",
                        "parameter_label": "Subject ID",
                    },
                    {
                        "endpoint": "procedures",
                        "description": (
                            "Retrieve procedures metadata from Labtracks and "
                            "SharePoint servers"
                        ),
                        "parameter": "subject_id",
                        "parameter_label": "Subject ID",
                    },
                ],
            }
        ),
    )
