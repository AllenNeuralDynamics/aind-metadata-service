"""Starts and runs a Flask Service"""

import os
from typing import Optional

from aind_metadata_mapper.bergamo.session import BergamoEtl
from aind_metadata_mapper.bergamo.session import (
    JobSettings as BergamoJobSettings,
)
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.concurrency import run_in_threadpool

from aind_metadata_service import __version__ as SERVICE_VERSION
from aind_metadata_service.client import StatusCodes
from aind_metadata_service.labtracks.client import (
    LabTracksClient,
    LabTracksSettings,
)
from aind_metadata_service.mgi.client import MgiClient, MgiSettings
from aind_metadata_service.mgi.mapping import MgiMapper
from aind_metadata_service.response_handler import EtlResponse
from aind_metadata_service.sharepoint.client import (
    SharePointClient,
    SharepointSettings,
)
from aind_metadata_service.slims.client import SlimsHandler, SlimsSettings
from aind_metadata_service.smartsheet.client import (
    FundingSmartsheetSettings,
    PerfusionsSmartsheetSettings,
    ProtocolsSmartsheetSettings,
    SmartSheetClient,
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

sharepoint_settings = SharepointSettings()
labtracks_settings = LabTracksSettings()

tars_settings = AzureSettings()

slims_settings = SlimsSettings()

funding_smartsheet_settings = FundingSmartsheetSettings()
perfusions_smartsheet_settings = PerfusionsSmartsheetSettings()
protocols_smartsheet_settings = ProtocolsSmartsheetSettings()

mgi_settings = MgiSettings()

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
slims_client = SlimsHandler(settings=slims_settings)
tars_client = TarsClient(azure_settings=tars_settings)
mgi_client = MgiClient(settings=mgi_settings)

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
async def retrieve_instrument(instrument_id, partial_match=False):
    """Retrieves instrument from slims"""
    model_response = slims_client.get_instrument_model_response(
        instrument_id, partial_match=partial_match
    )
    return model_response.map_to_json_response(validate=False)


@app.get("/rig/{rig_id}")
async def retrieve_rig(rig_id, partial_match=False):
    """Retrieves rig from slims"""
    model_response = slims_client.get_rig_model_response(
        rig_id, partial_match=partial_match
    )
    return model_response.map_to_json_response(validate=False)


@app.get("/slims/ecephys_sessions")
async def retrieve_slims_ecephys(
    subject_id: Optional[str] = Query(None, alias="subject_id"),
    session_name: Optional[str] = Query(
        None,
        alias="session_name",
        description="Name of the session",
    ),
    start_date_gte: Optional[str] = Query(
        None,
        alias="start_date_gte",
        description="Experiment run created on or after. (ISO format)",
    ),
    end_date_lte: Optional[str] = Query(
        None,
        alias="end_date_lte",
        description="Experiment run created on or before. (ISO format)",
    ),
):
    """Retrieves sessions from slims"""
    response = await run_in_threadpool(
        slims_client.get_slims_ecephys_response,
        subject_id=subject_id,
        session_name=session_name,
        start_date=start_date_gte,
        end_date=end_date_lte,
    )
    return response


@app.get("/protocols/{protocol_name}")
async def retrieve_protocols(
    protocol_name,
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
    return model_response.map_to_json_response()


@app.get("/mgi_allele/{allele_name}")
async def retrieve_mgi_allele(
    allele_name,
):
    """Retrieves allele information from mgi"""

    # TODO: We can probably cache the response if it's 200
    mgi_response = await run_in_threadpool(
        mgi_client.get_allele_info, allele_name=allele_name
    )
    mapper = MgiMapper(mgi_info=mgi_response)
    model_response = mapper.get_model_response()
    return model_response.map_to_json_response()


@app.get("/perfusions/{subject_id}")
async def retrieve_perfusions(subject_id):
    """Retrieves perfusion information from smartsheet"""

    # TODO: We can probably cache the response if it's 200
    smart_sheet_response = await run_in_threadpool(
        perfusions_smart_sheet_client.get_sheet
    )
    mapper = PerfusionsMapper(
        smart_sheet_response=smart_sheet_response, input_id=subject_id
    )
    model_response = mapper.get_model_response()
    return model_response.map_to_json_response()


@app.get("/funding/{project_name}")
async def retrieve_funding(project_name):
    """Retrieves funding information from smartsheet"""

    # TODO: We can probably cache the response if it's 200
    smart_sheet_response = await run_in_threadpool(
        funding_smart_sheet_client.get_sheet
    )
    mapper = FundingMapper(
        smart_sheet_response=smart_sheet_response, input_id=project_name
    )
    model_response = mapper.get_model_response()
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


@app.get("/slims/smartspim_imaging")
async def retrieve_smartspim_imaging(
    subject_id: Optional[str] = Query(None, alias="subject_id"),
    start_date_gte: Optional[str] = Query(
        None,
        alias="start_date_gte",
        description="Experiment run created on or after. (ISO format)",
    ),
    end_date_lte: Optional[str] = Query(
        None,
        alias="end_date_lte",
        description="Experiment run created on or before. (ISO format)",
    ),
):
    """
    Retrieves SPIM Imaging data from SLIMS server
    """
    response = await run_in_threadpool(
        slims_client.get_slims_imaging_response,
        subject_id=subject_id,
        start_date=start_date_gte,
        end_date=end_date_lte,
    )
    return response


@app.get("/slims/histology")
async def retrieve_slims_histology(
    subject_id: Optional[str] = Query(None, alias="subject_id"),
    start_date_gte: Optional[str] = Query(
        None,
        alias="start_date_gte",
        description="Experiment run created on or after. (ISO format)",
    ),
    end_date_lte: Optional[str] = Query(
        None,
        alias="end_date_lte",
        description="Experiment run created on or before. (ISO format)",
    ),
):
    """
    Retrieves Histology data from SLIMS server
    """
    response = await run_in_threadpool(
        slims_client.get_slims_histology_response,
        subject_id=subject_id,
        start_date=start_date_gte,
        end_date=end_date_lte,
    )
    return response


@app.get("/slims/water_restriction")
async def retrieve_slims_water_restriction(
    subject_id: Optional[str] = Query(None, alias="subject_id"),
    start_date_gte: Optional[str] = Query(
        None,
        alias="start_date_gte",
        description="Experiment run created on or after. (ISO format)",
    ),
    end_date_lte: Optional[str] = Query(
        None,
        alias="end_date_lte",
        description="Experiment run created on or before. (ISO format)",
    ),
):
    """
    Retrieves Water Restriction data from SLIMS server
    """
    response = await run_in_threadpool(
        slims_client.get_slims_water_restriction_response,
        subject_id=subject_id,
        start_date=start_date_gte,
        end_date=end_date_lte,
    )
    return response


@app.get("/slims/viral_injections")
async def retrieve_slims_injections(
    subject_id: Optional[str] = Query(None, alias="subject_id"),
    start_date_gte: Optional[str] = Query(
        None,
        alias="start_date_gte",
        description="Experiment run created on or after. (ISO format)",
    ),
    end_date_lte: Optional[str] = Query(
        None,
        alias="end_date_lte",
        description="Experiment run created on or before. (ISO format)",
    ),
):
    """
    Retrieves Viral Injection data from SLIMS server
    """
    response = await run_in_threadpool(
        slims_client.get_slims_viral_injection_response,
        subject_id=subject_id,
        start_date=start_date_gte,
        end_date=end_date_lte,
    )
    return response


@app.get("/subject/{subject_id}")
async def retrieve_subject(subject_id):
    """
    Retrieves subject from Labtracks server and adds alleles from MGI
    """
    lb_client = LabTracksClient.from_settings(labtracks_settings)
    model_response = await run_in_threadpool(
        lb_client.get_subject_info, subject_id=subject_id
    )
    if model_response.status_code == StatusCodes.DB_RESPONDED:
        for subject_model in model_response.aind_models:
            alleles = []
            genotype = subject_model.genotype
            allele_names = mgi_client.get_allele_names_from_genotype(
                genotype=genotype
            )
            for allele_name in allele_names:
                mgi_response = await run_in_threadpool(
                    mgi_client.get_allele_info, allele_name=allele_name
                )
                mapper = MgiMapper(mgi_info=mgi_response)
                mgi_model_response = mapper.get_model_response()
                if mgi_model_response.status_code == 200:
                    allele = mgi_model_response.aind_models[0]
                    alleles.append(allele)
                subject_model.alleles = alleles
    return model_response.map_to_json_response()


@app.get("/tars_injection_materials/{prep_lot_number}")
async def retrieve_injection_materials(prep_lot_number):
    """
    Retrieves injection materials from TARS server
    """
    model_response = await run_in_threadpool(
        tars_client.get_injection_materials_info,
        prep_lot_number=prep_lot_number,
    )
    # TODO: move molecules call to here
    return model_response.map_to_json_response()


@app.get("/intended_measurements/{subject_id}")
async def retrieve_intended_measurements(subject_id):
    """
    Retrieves intended measurements from SLIMS server
    """
    sharepoint_client = SharePointClient.from_settings(sharepoint_settings)
    model_response = await run_in_threadpool(
        sharepoint_client.get_intended_measurement_info, subject_id=subject_id
    )
    return model_response.map_to_json_response()


@app.get("/procedures/{subject_id}")
async def retrieve_procedures(subject_id):
    """
    Retrieves procedure info from SharePoint and Labtracks servers
    """
    sharepoint_client = SharePointClient.from_settings(sharepoint_settings)
    lb_client = LabTracksClient.from_settings(labtracks_settings)
    lb_response = await run_in_threadpool(
        lb_client.get_procedures_info, subject_id=subject_id
    )
    sp2019_response = await run_in_threadpool(
        sharepoint_client.get_procedure_info,
        subject_id=subject_id,
        list_id=sharepoint_settings.nsb_2019_list_id,
    )
    sp2023_response = await run_in_threadpool(
        sharepoint_client.get_procedure_info,
        subject_id=subject_id,
        list_id=sharepoint_settings.nsb_2023_list_id,
    )
    sp2025_response = await run_in_threadpool(
        sharepoint_client.get_procedure_info,
        subject_id=subject_id,
        list_id=sharepoint_settings.nsb_present_list_id,
    )
    las2020_response = await run_in_threadpool(
        sharepoint_client.get_procedure_info,
        subject_id=subject_id,
        list_id=sharepoint_settings.las_2020_list_id,
    )
    slims_wr_response = await run_in_threadpool(
        slims_client.get_water_restriction_procedures_model_response,
        subject_id=subject_id,
    )
    smartsheet_perfusions_response = await run_in_threadpool(
        perfusions_smart_sheet_client.get_sheet
    )
    mapper = PerfusionsMapper(
        smart_sheet_response=smartsheet_perfusions_response,
        input_id=subject_id,
    )
    smartsheet_model_response = mapper.get_procedures_model_response()
    # merge subject procedures
    merged_response = sharepoint_client.merge_responses(
        [
            lb_response,
            sp2019_response,
            sp2023_response,
            sp2025_response,
            las2020_response,
            slims_wr_response,
            smartsheet_model_response,
        ]
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
    smartsheet_protocols_response = await run_in_threadpool(
        protocols_smart_sheet_client.get_sheet
    )
    protocols_integrator = ProtocolsIntegrator()
    protocols_list = protocols_integrator.get_protocols_list(
        integrated_response
    )
    protocols_mapping = {}
    for protocol_name in protocols_list:
        mapper = ProtocolsMapper(
            smart_sheet_response=smartsheet_protocols_response,
            input_id=protocol_name,
        )
        model_response = mapper.get_model_response()
        protocols_mapping[protocol_name] = (
            model_response.map_to_json_response()
        )
    integrated_response = protocols_integrator.integrate_protocols(
        response=integrated_response, protocols_mapping=protocols_mapping
    )
    slims_hist_response = await run_in_threadpool(
        slims_client.get_histology_procedures_model_response,
        subject_id=subject_id,
    )
    merged_response = sharepoint_client.merge_responses(
        [integrated_response, slims_hist_response]
    )
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
