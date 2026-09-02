"""Starts and runs a FastAPI Server"""

import logging
import os
import warnings

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from aind_metadata_service_server import __version__ as service_version
from aind_metadata_service_server.routes import (
    dataverse,
    funding,
    healthcheck,
    index,
    injection_materials,
    intended_measurements,
    mgi_allele,
    perfusion,
    procedures,
    protocol,
    rig_and_instrument,
    subject,
    user_email,
    v1_proxy,
)

warnings.filterwarnings(
    "ignore", category=UserWarning, message=r".*Pydantic serializer warnings.*"
)

# The log level can be set by adding an environment variable before launch.
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=log_level)

description = """
## aind-metadata-service

Service to pull data from example backend.

"""


def set_operation_ids(router: APIRouter) -> None:
    """
    Set operation_id to route name for all APIRoutes in a router.

    This cleans up the auto-generated operation IDs in OpenAPI spec.

    Parameters
    ----------
    router : APIRouter
        The router whose routes should have operation_ids set
    """
    for route in router.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name


# noinspection PyTypeChecker
app = FastAPI(
    title="aind-metadata-service",
    description=description,
    summary="Serves data from various databases at AIND.",
    version=service_version,
)

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Set operation IDs for each router before including
routers = [
    v1_proxy.router,
    healthcheck.router,
    funding.router,
    intended_measurements.router,
    procedures.router,
    protocol.router,
    rig_and_instrument.router,
    subject.router,
    perfusion.router,
    mgi_allele.router,
    injection_materials.router,
    dataverse.router,
    user_email.router,
    index.router,
]

for router in routers:
    set_operation_ids(router)
    app.include_router(router)
