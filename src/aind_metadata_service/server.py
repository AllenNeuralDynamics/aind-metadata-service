"""Starts and runs a Flask Service"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette.concurrency import run_in_threadpool

from aind_metadata_service.labtracks.client import (
    LabTracksClient,
    LabTracksSettings,
)
from aind_metadata_service.sharepoint.client import (
    SharePointClient,
    SharepointSettings,
)
from aind_metadata_service.smartsheet.client import (
    SmartSheetClient,
    SmartsheetSettings,
)
from aind_metadata_service.smartsheet.funding.mapping import FundingMapper
from aind_metadata_service.smartsheet.perfusions.mapping import (
    PerfusionsMapper,
)

SMARTSHEET_FUNDING_ID = os.getenv("SMARTSHEET_FUNDING_ID")
SMARTSHEET_FUNDING_TOKEN = os.getenv("SMARTSHEET_FUNDING_TOKEN")

SMARTSHEET_PERFUSIONS_ID = os.getenv("SMARTSHEET_PERFUSIONS_ID")
SMARTSHEET_PERFUSIONS_TOKEN = os.getenv("SMARTSHEET_PERFUSIONS_TOKEN")

# TODO: Move client instantiation when the server starts instead of creating
#  one for each request?
sharepoint_settings = SharepointSettings()
labtracks_settings = LabTracksSettings()
funding_smartsheet_settings = SmartsheetSettings(
    access_token=SMARTSHEET_FUNDING_TOKEN, sheet_id=SMARTSHEET_FUNDING_ID
)
perfusions_smartsheet_settings = SmartsheetSettings(
    access_token=SMARTSHEET_PERFUSIONS_TOKEN, sheet_id=SMARTSHEET_PERFUSIONS_ID
)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# TODO: Handle favicon better?
favicon_path = os.getenv("FAVICON_PATH")

perfusions_smart_sheet_client = SmartSheetClient(
    smartsheet_settings=perfusions_smartsheet_settings
)

funding_smart_sheet_client = SmartSheetClient(
    smartsheet_settings=funding_smartsheet_settings
)


@app.get("/perfusions/{subject_id}")
async def retrieve_perfusions(subject_id, pickle: bool = False):
    """Retrieves perfusion information from smartsheet"""

    # TODO: We can probably cache perfusions sheet
    mapper = PerfusionsMapper(smart_sheet_client=perfusions_smart_sheet_client)
    model_response = await run_in_threadpool(
        mapper.get_model_response, input_id=subject_id
    )
    if pickle:
        return model_response.map_to_pickled_response()
    else:
        return model_response.map_to_json_response()


@app.get("/funding/{project_id}")
async def retrieve_funding(project_id, pickle: bool = False):
    """Retrieves funding information from smartsheet"""

    # TODO: We can probably cache funding sheet
    mapper = FundingMapper(smart_sheet_client=funding_smart_sheet_client)
    model_response = await run_in_threadpool(
        mapper.get_model_response, input_id=project_id
    )
    if pickle:
        return model_response.map_to_pickled_response()
    else:
        return model_response.map_to_json_response()


@app.get("/subject/{subject_id}")
async def retrieve_subject(subject_id, pickle: bool = False):
    """
    Retrieves subject from Labtracks server
    Returns pickled data if URL parameter pickle=True, else returns json
    """
    lb_client = LabTracksClient.from_settings(labtracks_settings)
    model_response = await run_in_threadpool(
        lb_client.get_subject_info, subject_id=subject_id
    )
    if pickle:
        return model_response.map_to_pickled_response()
    else:
        return model_response.map_to_json_response()


@app.get("/procedures/{subject_id}")
async def retrieve_procedures(subject_id, pickle: bool = False):
    """
    Retrieves procedure info from SharePoint and Labtracks servers
    Returns pickled data if URL parameter pickle=True, else returns json
    """
    sharepoint_client = SharePointClient.from_settings(sharepoint_settings)
    lb_client = LabTracksClient.from_settings(labtracks_settings)
    lb_response = await run_in_threadpool(
        lb_client.get_procedures_info, subject_id=subject_id
    )
    sp2019_response = await run_in_threadpool(
        sharepoint_client.get_procedure_info,
        subject_id=subject_id,
        list_title=sharepoint_settings.nsb_2019_list,
    )
    sp2023_response = await run_in_threadpool(
        sharepoint_client.get_procedure_info,
        subject_id=subject_id,
        list_title=sharepoint_settings.nsb_2023_list,
    )
    merged_response = sharepoint_client.merge_responses(
        [lb_response, sp2019_response, sp2023_response]
    )
    if pickle:
        return merged_response.map_to_pickled_response()
    else:
        return merged_response.map_to_json_response()


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
