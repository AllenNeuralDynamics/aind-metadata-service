"""Starts and runs a FastAPI Server"""

import os

from fastapi import FastAPI, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import logging
from aind_metadata_service import __version__ as SERVICE_VERSION

logging.basicConfig(level="INFO")

description = f"""
aind-metadata-service

Consolidates metadata from disparate databases:

LabTracks

SharePoint

  NSB
  
SLIMS

TARS

"""

app = FastAPI(
    title="aind-metadata-service",
    description=description,
    summary="Consolidates metadata from disparate databases.",
    version=SERVICE_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# TODO: Handle favicon better?
favicon_path = os.getenv("FAVICON_PATH")

template_directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "templates")
)
templates = Jinja2Templates(directory=template_directory)


@app.get("/subject/{subject_id}")
def retrieve_subject(subject_id: str = Path(..., example="632269")):
    """
    Retrieves subject information from LabTracks.
    """
    return {"subject_id": subject_id}


@app.get(
    "/favicon.ico",
    include_in_schema=False,
    response_class=RedirectResponse,
    status_code=200,
)
async def favicon():
    """
    Returns the favicon
    """
    return favicon_path
