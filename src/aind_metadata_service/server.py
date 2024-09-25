"""Starts and runs a Flask Service"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aind_metadata_service.labtracks.client import (
    LabTracksClient,
)
from aind_metadata_service.labtracks.query_builder import LabTracksQueries

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# TODO: Handle favicon better?
favicon_path = os.getenv("FAVICON_PATH")


lb_client = LabTracksClient(settings=labtracks_settings)


@app.get("/labtracks/{subject_id}")
async def retrieve_labtracks_info(subject_id: str, table: str):

    # TODO: Sanitize user input
    if table == "subject":
        query = LabTracksQueries.subject_from_subject_id(subject_id)
    else:
        query = LabTracksQueries.procedures_from_subject_id(subject_id)
    response = lb_client.run_query(query)
    return response


