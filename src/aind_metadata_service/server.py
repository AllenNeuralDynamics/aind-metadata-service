"""Starts and runs a FastAPI Server"""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aind_metadata_service import __version__ as service_version
from aind_metadata_service.routers.favicon.route import router as fv_router
from aind_metadata_service.routers.funding.route import router as fund_router
from aind_metadata_service.routers.healthcheck.route import router as hc_router
from aind_metadata_service.routers.project_names.route import (
    router as pn_router,
)
from aind_metadata_service.routers.subject.route import router as subj_router

log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=log_level)

description = """
## aind-metadata-service

Here is a list of databases we're pulling data from:

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
    version=service_version,
)

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


app.include_router(subj_router)
app.include_router(fund_router)
app.include_router(fv_router)
app.include_router(pn_router)
app.include_router(hc_router)
