"""Starts and runs a Flask Service"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from aind_metadata_service.labtracks.client import (
    LabTracksClient,
    LabTracksSettings,
)
from aind_metadata_service.sharepoint.client import (
    SharePointClient,
    SharepointSettings,
)

sharepoint_settings = SharepointSettings()
labtracks_settings = LabTracksSettings()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# TODO: Handle favicon better?
favicon_path = os.getenv("FAVICON_PATH")


@app.get("/subject/{subject_id}")
async def retrieve_subject(subject_id, pickle=False):
    """
    Retrieves subject from Labtracks server
    TODO: pickle option will be handled in future versions
    """
    lb_client = LabTracksClient.from_settings(labtracks_settings)
    response = lb_client.get_subject_info(subject_id)
    json_response = response.map_to_json_response()
    return json_response


@app.get("/procedures/{subject_id}")
async def retrieve_procedures(subject_id, pickle=False):
    """
    Retrieves procedure info from SharePoint
    TODO: pickle option will be handled in future versions
    """
    sharepoint_client = SharePointClient.from_settings(sharepoint_settings)
    lb_client = LabTracksClient.from_settings(labtracks_settings)
    lb_response = lb_client.get_procedures_info(subject_id=subject_id)
    sp2019_response = sharepoint_client.get_procedure_info(
        subject_id=subject_id, list_title=sharepoint_settings.nsb_2019_list
    )
    sp2023_response = sharepoint_client.get_procedure_info(
        subject_id=subject_id, list_title=sharepoint_settings.nsb_2023_list
    )
    merged_response = sharepoint_client.merge_responses(
        [lb_response, sp2019_response, sp2023_response]
    )
    json_response = merged_response.map_to_json_response()
    return json_response


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
