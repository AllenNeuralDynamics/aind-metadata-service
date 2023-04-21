"""Starts and runs a Flask Service"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from aind_metadata_service.labtracks.client import LabTracksClient
from aind_metadata_service.sharepoint.client import SharePointClient

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# TODO: Handle configs better?
favicon_path = os.getenv("FAVICON_PATH")

labtracks_driver = os.getenv("ODBC_DRIVER")
labtracks_server = os.getenv("LABTRACKS_SERVER")
labtracks_port = os.getenv("LABTRACKS_PORT")
labtracks_db = os.getenv("LABTRACKS_DATABASE")
labtracks_user = os.getenv("LABTRACKS_USER")
labtracks_password = os.getenv("LABTRACKS_PASSWORD")

sharepoint_url = os.getenv("SHAREPOINT_URL")
sharepoint_user = os.getenv("SHAREPOINT_USER")
sharepoint_password = os.getenv("SHAREPOINT_PASSWORD")


@app.get("/subject/{subject_id}")
async def retrieve_subject(subject_id):
    """
    Retrieves subject from Labtracks server
    """
    lb_client = LabTracksClient(
        driver=labtracks_driver,
        server=labtracks_server,
        port=labtracks_port,
        db=labtracks_db,
        user=labtracks_user,
        password=labtracks_password,
    )
    response = lb_client.get_subject_info(subject_id)
    return response


@app.get("/procedures/{subject_id}")
async def retrieve_procedures(subject_id):
    """
    Retrieves procedure info from SharePoint
    """
    sharepoint_client = SharePointClient(
        site_url=sharepoint_url,
        client_id=sharepoint_user,
        client_secret=sharepoint_password,
    )

    response = sharepoint_client.get_procedure_info(subject_id=subject_id)

    return response


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
