"""Starts and runs a FastAPI Server"""

import logging
import os
import warnings

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from aind_metadata_service_server import __version__ as service_version
from aind_metadata_service_server.routes import (
    healthcheck,
    index,
    subject,
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

app.include_router(v1_proxy.router)
app.include_router(healthcheck.router)
app.include_router(subject.router)
app.include_router(index.router)

# Clean up the methods names that is generated in the client code
for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name
