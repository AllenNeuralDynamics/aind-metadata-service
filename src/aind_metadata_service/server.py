"""Starts and runs a FastAPI Server"""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aind_metadata_service import __version__ as service_version
from aind_metadata_service.backends.redis.session import lifespan
from aind_metadata_service.routers.favicon.route import router as fv_router
from aind_metadata_service.routers.funding.route import router as fn_router
from aind_metadata_service.routers.healthcheck.route import router as hc_router
from aind_metadata_service.routers.injection_materials.route import (
    router as inj_router,
)
from aind_metadata_service.routers.perfusions.route import router as pf_router
from aind_metadata_service.routers.project_names.route import (
    router as pn_router,
)
from aind_metadata_service.routers.protocols.route import router as pt_router
from aind_metadata_service.routers.subject.route import router as subj_router
from aind_metadata_service.routers.rig.route import router as rig_router
from aind_metadata_service.routers.instrument.route import router as ins_router

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

# noinspection PyTypeChecker
app = FastAPI(
    title="aind-metadata-service",
    description=description,
    summary="Consolidates metadata from disparate databases.",
    version=service_version,
    lifespan=lifespan,
)

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(subj_router)
app.include_router(fn_router)
app.include_router(pf_router)
app.include_router(pt_router)
app.include_router(fv_router)
app.include_router(pn_router)
app.include_router(hc_router)
app.include_router(inj_router)
app.include_router(rig_router)
app.include_router(ins_router)
