"""Starts and runs a Flask Service"""

import os

from fastapi import FastAPI

from aind_metadata_service.labtracks.client import LabTracksClient
from aind_metadata_service.labtracks.query_builder import LabTracksQueries


app = FastAPI()

# TODO: Handle configs better?

driver = os.getenv("ODBC_DRIVER")
server = os.getenv("LABTRACKS_SERVER")
port = os.getenv("LABTRACKS_PORT")
db = os.getenv("LABTRACKS_DATABASE")
user = os.getenv("LABTRACKS_USER")
password = os.getenv("LABTRACKS_PASSWORD")


@app.get("/subject/{subject_id}")
async def retrieve_subject(subject_id):
    """
    Retrieves subject from Labtracks server
    """
    lb_client = LabTracksClient(
        driver=driver,
        server=server,
        port=port,
        db=db,
        user=user,
        password=password,
    )
    query = LabTracksQueries.subject_from_subject_id(subject_id)
    session = lb_client.create_session()
    lb_response = lb_client.submit_query(session, query)
    lb_client.close_session(session)
    handled_response = lb_client.handle_response(lb_response)

    return handled_response
