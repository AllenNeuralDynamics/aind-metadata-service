"""Starts and runs a Flask Service"""

import os

from fastapi import FastAPI

from aind_metadata_service.labtracks.client import LabTracksClient
from aind_metadata_service.labtracks.query_builder import LabTracksQueries
from aind_metadata_service.sharepoint.client import SharePointClient

app = FastAPI()

# TODO: Handle configs better?

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
    query = LabTracksQueries.subject_from_subject_id(subject_id)
    session = lb_client.create_session()
    lb_response = lb_client.submit_query(session, query)
    lb_client.close_session(session)
    handled_response = lb_client.handle_response(lb_response)

    return handled_response


@app.get("/procedures/{subject_id}")
async def retrieve_procedures(subject_id):
    """
    Retrieves procedure info from SharePoint
    """
    sharepoint_client = SharePointClient(
        site_url=sharepoint_url,
        client_id=sharepoint_user,
        client_secret=sharepoint_password
    )

    response = sharepoint_client.get_procedure_info(subject_id=subject_id)

    return response
