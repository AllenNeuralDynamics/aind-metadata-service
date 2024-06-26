"""Starts and runs a Flask Service"""

import os

from aind_metadata_mapper.bergamo.session import BergamoEtl
from aind_metadata_mapper.bergamo.session import (
    JobSettings as BergamoJobSettings,
)
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.concurrency import run_in_threadpool

from aind_metadata_service import __version__ as SERVICE_VERSION
from aind_metadata_service.labtracks.client import (
    LabTracksClient,
    LabTracksSettings,
)
from aind_metadata_service.response_handler import EtlResponse
from aind_metadata_service.sharepoint.client import (
    SharePointClient,
    SharepointSettings,
)
from aind_metadata_service.slims.client import SlimsClient, SlimsSettings
from aind_metadata_service.smartsheet.client import (
    SmartSheetClient,
    SmartsheetSettings,
)
from aind_metadata_service.smartsheet.funding.mapping import FundingMapper
from aind_metadata_service.smartsheet.perfusions.mapping import (
    PerfusionsMapper,
)
from aind_metadata_service.smartsheet.protocols.mapping import (
    ProtocolsIntegrator,
    ProtocolsMapper,
)
from aind_metadata_service.tars.client import AzureSettings, TarsClient
from aind_metadata_service.tars.mapping import TarsResponseHandler

SMARTSHEET_FUNDING_ID = os.getenv("SMARTSHEET_FUNDING_ID")
SMARTSHEET_FUNDING_TOKEN = os.getenv("SMARTSHEET_API_TOKEN")

SMARTSHEET_PERFUSIONS_ID = os.getenv("SMARTSHEET_PERFUSIONS_ID")
SMARTSHEET_PERFUSIONS_TOKEN = os.getenv("SMARTSHEET_API_TOKEN")

SMARTSHEET_PROTOCOLS_ID = os.getenv("SMARTSHEET_PROTOCOLS_ID")
SMARTSHEET_PROTOCOLS_TOKEN = os.getenv("SMARTSHEET_API_TOKEN")

# TODO: Move client instantiation when the server starts instead of creating
#  one for each request?
sharepoint_settings = SharepointSettings()
labtracks_settings = LabTracksSettings()
tars_settings = AzureSettings()
slims_settings = SlimsSettings()

funding_smartsheet_settings = SmartsheetSettings(
    access_token=SMARTSHEET_FUNDING_TOKEN, sheet_id=SMARTSHEET_FUNDING_ID
)
perfusions_smartsheet_settings = SmartsheetSettings(
    access_token=SMARTSHEET_PERFUSIONS_TOKEN, sheet_id=SMARTSHEET_PERFUSIONS_ID
)

protocols_smartsheet_settings = SmartsheetSettings(
    access_token=SMARTSHEET_PROTOCOLS_TOKEN, sheet_id=SMARTSHEET_PROTOCOLS_ID
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

protocols_smart_sheet_client = SmartSheetClient(
    smartsheet_settings=protocols_smartsheet_settings
)

tars_client = TarsClient(azure_settings=tars_settings)
slims_client = SlimsClient(settings=slims_settings)

template_directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "templates")
)
templates = Jinja2Templates(directory=template_directory)


@app.post("/bergamo_session/")
async def retrieve_bergamo_session(job_settings: BergamoJobSettings):
    """Builds a bergamo session model from the given job settings"""

    etl_job = BergamoEtl(
        job_settings=job_settings,
    )
    response = etl_job.run_job()
    return EtlResponse.map_job_response(response)


@app.get("/instrument/{instrument_id}")
async def retrieve_instrument(instrument_id, pickle: bool = False):
    """
    Retrieves instrument from slims
    Returns pickled data if URL parameter pickle=True, else returns json
    """
    model_response = slims_client.get_instrument_model_response(instrument_id)
    if pickle:
        return model_response.map_to_pickled_response()
    else:
        return model_response.map_to_json_response(validate=False)


@app.get("/rig/{rig_id}")
async def retrieve_rig(rig_id, pickle: bool = False):
    """
    Retrieves rig from slims
    Returns pickled data if URL parameter pickle=True, else returns json
    """
    model_response = slims_client.get_rig_model_response(rig_id)
    if pickle:
        return model_response.map_to_pickled_response()
    else:
        return model_response.map_to_json_response(validate=False)


@app.get("/protocols/{protocol_name}")
async def retrieve_protocols(
    protocol_name,
    pickle: bool = False,
):
    """Retrieves perfusion information from smartsheet"""

    # TODO: We can probably cache the response if it's 200
    smart_sheet_response = await run_in_threadpool(
        protocols_smart_sheet_client.get_sheet
    )
    mapper = ProtocolsMapper(
        smart_sheet_response=smart_sheet_response, input_id=protocol_name
    )
    model_response = mapper.get_model_response()

    if pickle:
        return model_response.map_to_pickled_response()
    else:
        return model_response.map_to_json_response()


@app.get("/perfusions/{subject_id}")
async def retrieve_perfusions(subject_id, pickle: bool = False):
    """Retrieves perfusion information from smartsheet"""

    # TODO: We can probably cache the response if it's 200
    smart_sheet_response = await run_in_threadpool(
        perfusions_smart_sheet_client.get_sheet
    )
    mapper = PerfusionsMapper(
        smart_sheet_response=smart_sheet_response, input_id=subject_id
    )
    model_response = mapper.get_model_response()

    if pickle:
        return model_response.map_to_pickled_response()
    else:
        return model_response.map_to_json_response()


@app.get("/funding/{project_name}")
async def retrieve_funding(project_name, pickle: bool = False):
    """Retrieves funding information from smartsheet"""

    # TODO: We can probably cache the response if it's 200
    smart_sheet_response = await run_in_threadpool(
        funding_smart_sheet_client.get_sheet
    )
    mapper = FundingMapper(
        smart_sheet_response=smart_sheet_response, input_id=project_name
    )
    model_response = mapper.get_model_response()
    if pickle:
        return model_response.map_to_pickled_response()
    else:
        return model_response.map_to_json_response()


@app.get("/project_names")
async def retrieve_project_names():
    """Retrieves funding information from smartsheet"""

    # TODO: We can probably cache the response if it's 200
    smart_sheet_response = await run_in_threadpool(
        funding_smart_sheet_client.get_sheet
    )
    mapper = FundingMapper(
        smart_sheet_response=smart_sheet_response, input_id=""
    )
    json_response = mapper.get_project_names()
    return json_response


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


@app.get("/tars_injection_materials/{prep_lot_number}")
async def retrieve_injection_materials(prep_lot_number, pickle: bool = False):
    """
    Retrieves injection materials from TARS server
    Returns pickled data if URL parameter pickle=True, else returns json
    """
    model_response = await run_in_threadpool(
        tars_client.get_injection_materials_info,
        prep_lot_number=prep_lot_number,
    )
    # TODO: move molecules call to here
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
    las2020_response = await run_in_threadpool(
        sharepoint_client.get_procedure_info,
        subject_id=subject_id,
        list_title=sharepoint_settings.las_2020_list,
    )
    merged_response = sharepoint_client.merge_responses(
        [lb_response, sp2019_response, sp2023_response, las2020_response]
    )
    # integrate TARS response
    mapper = TarsResponseHandler()
    viruses = mapper.get_virus_strains(merged_response)
    tars_mapping = {}
    for virus_strain in viruses:
        tars_response = await retrieve_injection_materials(
            prep_lot_number=virus_strain
        )
        tars_mapping[virus_strain] = tars_response
    integrated_response = mapper.integrate_injection_materials(
        response=merged_response, tars_mapping=tars_mapping
    )
    # integrate protocols from smartsheet
    smart_sheet_response = await run_in_threadpool(
        protocols_smart_sheet_client.get_sheet
    )
    protocols_integrator = ProtocolsIntegrator()
    protocols_list = protocols_integrator.get_protocols_list(
        integrated_response
    )
    protocols_mapping = {}
    for protocol_name in protocols_list:
        mapper = ProtocolsMapper(
            smart_sheet_response=smart_sheet_response, input_id=protocol_name
        )
        model_response = mapper.get_model_response()
        # smartsheet_response = await retrieve_protocols(
        #     protocol_name=protocol_name
        # )
        protocols_mapping[protocol_name] = (
            model_response.map_to_json_response()
        )
    integrated_response = protocols_integrator.integrate_protocols(
        response=integrated_response, protocols_mapping=protocols_mapping
    )
    if pickle:
        return integrated_response.map_to_pickled_response()
    else:
        return integrated_response.map_to_json_response()


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


@app.get("/")
async def index(request: Request):
    """
    Returns the index page with search UIs for enabled endpoints.
    """
    return templates.TemplateResponse(
        name="index.html",
        context=(
            {
                "request": request,  # required
                "service_name": "AIND Metadata Service",  # required
                "service_description": (
                    "REST service to retrieve metadata from AIND databases."
                ),
                "service_version": SERVICE_VERSION,
                "endpoints": [
                    {
                        "endpoint": "subject",  # required
                        "description": (
                            "Retrieve subject metadata from Labtracks server"
                        ),
                        "parameter": "subject_id",  # required
                        "parameter_label": "Subject ID",
                    },
                    {
                        "endpoint": "procedures",  # required
                        "description": (
                            "Retrieve procedures metadata from Labtracks and"
                            " SharePoint servers"
                        ),
                        "parameter": "subject_id",  # required
                        "parameter_label": "Subject ID",
                    },
                ],
            }
        ),
    )
