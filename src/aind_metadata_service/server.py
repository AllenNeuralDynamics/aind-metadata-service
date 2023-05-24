"""Starts and runs a Flask Service"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from aind_metadata_service.labtracks.client import LabTracksClient
from aind_metadata_service.response_handler import Responses
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

nsb_sharepoint_url = os.getenv("NSB_SHAREPOINT_URL")
nsb_sharepoint_list_2019 = os.getenv("NSB_2019_LIST", default="SWR 2019-2022")
nsb_sharepoint_list_2023 = os.getenv(
    "NSB_2023_LIST", default="SWR 2023-Present"
)
nsb_sharepoint_user = os.getenv("NSB_SHAREPOINT_USER")
nsb_sharepoint_password = os.getenv("NSB_SHAREPOINT_PASSWORD")


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
        nsb_site_url=nsb_sharepoint_url,
        nsb_list_title_2019=nsb_sharepoint_list_2019,
        nsb_list_title_2023=nsb_sharepoint_list_2023,
        client_id=nsb_sharepoint_user,
        client_secret=nsb_sharepoint_password,
    )
    lb_client = LabTracksClient(
        driver=labtracks_driver,
        server=labtracks_server,
        port=labtracks_port,
        db=labtracks_db,
        user=labtracks_user,
        password=labtracks_password,
    )
    lb_response = lb_client.get_procedures_info(subject_id=subject_id)
    sp_response = sharepoint_client.get_procedure_info(subject_id=subject_id)
    response = Responses.combine_procedure_responses(lb_response, sp_response)
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
