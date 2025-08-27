"""Maps information to aind-data-schema Procedures model."""

import logging
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Union

from aind_data_schema.core.procedures import (
    Procedures,
    Surgery,
)
from aind_data_schema.components.injection_procedures import Injection
from aind_data_schema.components.surgery_procedures import (
    BrainInjection
)
from aind_data_schema_models.mouse_anatomy import InjectionTargets
from aind_data_schema.components.subject_procedures import (
    Perfusion,
)
from aind_data_schema_models.units import MassUnit
from aind_labtracks_service_async_client.models import Task as LabTracksTask
from aind_sharepoint_service_async_client.models import (
    Las2020List,
    NSB2019List,
    NSB2023List,
)
from aind_slims_service_async_client.models import (
    SlimsHistologyData,
    SlimsWaterRestrictionData,
)
from aind_smartsheet_service_async_client.models import PerfusionsModel

from aind_metadata_service_server.mappers.las2020 import (
    MappedLASList as MappedLAS2020,
)

class LabTracksTaskStatuses(Enum):
    """LabTracks Task Status Options"""

    FINISHED = "F"
    SCHEDULED = "S"
    CANCELLED = "C"
    DELETED = "D"
    ACCEPTED = "A"
    DECLINED = "L"


class LabTracksProcedures(Enum):
    """Keywords for LabTracks procedures"""

    PERFUSION = "Perfusion"
    RO_INJECTION = "RO Injection"


class ProtocolNames(Enum):
    """Enum of Protocol Names in Smartsheet"""

    IMMUNOLABELING = "Immunolabeling of a Whole Mouse Brain"
    DELIPIDATION = (
        "Tetrahydrofuran and Dichloromethane Delipidation of a"
        " Whole Mouse Brain"
    )
    SBIP_DELIPADATION = "Aqueous (SBiP) Delipidation of a Whole Mouse Brain"
    GELATIN_PREVIOUS = (
        "Whole Mouse Brain Delipidation, Immunolabeling,"
        " and Expansion Microscopy"
    )
    INJECTION_NANOJECT = "Injection of Viral Tracers by Nanoject V.4"
    INJECTION_IONTOPHORESIS = (
        "Stereotaxic Surgery for Delivery of Tracers by Iontophoresis V.3"
    )
    PERFUSION = "Mouse Cardiac Perfusion Fixation and Brain Collection V.5"
    SMARTSPIM_IMAGING = "Imaging cleared mouse brains on SmartSPIM"
    SMARTSPIM_SETUP = "SmartSPIM setup and alignment"
    SURGERY = "General Set-Up and Take-Down for Rodent Neurosurgery"
    PROTOCOL_COLLECTION = (
        "Protocol Collection: Perfusing, Sectioning, IHC,"
        " Mounting and Coverslipping Mouse Brain Specimens"
    )
    SECTIONING = "Sectioning Mouse Brain with Sliding Microtome"
    MOUNTING_COVERSLIPPING = "Mounting and Coverslipping Mouse Brain Sections"
    IHC_SECTIONS = "Immunohistochemistry (IHC) Staining Mouse Brain Sections"
    DAPI_STAINING = "DAPI Staining Mouse Brain Sections"
    DURAGEL_APPLICATION = (
        "Duragel application for acute electrophysiological recordings"
    )


class ProceduresMapper:
    """Class to handle mapping of procedures data."""

    def __init__(
        self,
        labtracks_tasks: List[LabTracksTask] = [],
        las_2020: List[Las2020List] = [],
    ):
        """
        Class constructor.
        Parameters
        ----------
        labtracks_tasks :  List[LabTracksTask]
        """
        self.labtracks_tasks = labtracks_tasks
        self.las_2020 = las_2020

    @staticmethod
    def _map_labtracks_task_to_aind_surgery(
        task: LabTracksTask,
    ) -> Union[Surgery, None]:
        """
        Helper method to map a single LabTracksTask to a Surgery object.

        Parameters
        ----------
        task : LabTracksTask
            The task to map to a Surgery object

        Returns
        -------
        Union[Surgery, None]
            A mapped Surgery object or None if not applicable
        """
        start_date = task.date_start
        if start_date:
            start_date = start_date.date()

        end_date = task.date_end
        if end_date:
            end_date = end_date.date()

        experimenter_full_name = (
            str(task.investigator_id) if task.investigator_id else None
        )
        iacuc_protocol = (
            str(task.protocol_number) if task.protocol_number else None
        )
        type_name = task.type_name
        task_status = task.task_status

        if not (
            type_name and task_status == LabTracksTaskStatuses.FINISHED.value
        ):
            return None

        if LabTracksProcedures.PERFUSION.value.lower() in type_name.lower():
            output_specimen_ids = (
                {str(task.task_object)} if task.task_object else set()
            )

            return Surgery.model_construct(
                start_date=start_date,
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight_prior=None,
                animal_weight_post=None,
                anaesthesia=None,
                notes=None,
                procedures=[
                    Perfusion.model_construct(
                        output_specimen_ids=output_specimen_ids
                    )
                ],
            )

        elif (
            LabTracksProcedures.RO_INJECTION.value.lower() in type_name.lower()
        ):
            return Surgery.model_construct(
                start_date=start_date,
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight_prior=None,
                animal_weight_post=None,
                anaesthesia=None,
                notes=None,
                procedures=[
                    Injection.model_construct(
                        targeted_structure=InjectionTargets.RETRO_ORBITAL,
                        injection_volume=None, injection_eye=None
                    )
                ],
            )

        return None

    @staticmethod
    def map_sharepoint_response_to_aind_surgeries(
        response: List, mapper_cls: type, subject_id: Optional[str] = None
    ) -> List[Surgery]:
        """
        Generic method to map SharePoint data to Surgery objects
        using the provided mapper class.

        Parameters
        ----------
        response : List
            List of SharePoint model objects to map
        mapper_cls : Type
            The mapper class to use for mapping
        subject_id : Optional[str]
            Subject ID required for LAS2020 mapping

        Returns
        -------
        List[Surgery]
            A list of mapped Surgery objects
        """
        surgeries = []
        for item in response:
            mapped_model = mapper_cls(item)
            if isinstance(mapped_model, MappedLAS2020):
                procedure = mapped_model.get_surgery(subject_id)
                procedures = [procedure] if procedure else []
            else:
                procedures = mapped_model.get_surgeries()
            surgeries.extend(procedures)

        return surgeries

    def map_responses_to_aind_procedures(
        self, subject_id: str
    ) -> Union[Procedures, None]:
        """
        Maps all data sources to a complete Procedures model.

        Parameters
        ----------
        subject_id : str
            The subject ID for the procedures

        Returns
        -------
        Procedures
            Complete procedures model with all surgeries
        """
        subject_procedures = []
        specimen_procedures = []
        if self.labtracks_tasks:
            labtracks_surgeries = [
                self._map_labtracks_task_to_aind_surgery(task)
                for task in self.labtracks_tasks
                if self._map_labtracks_task_to_aind_surgery(task) is not None
            ]
            subject_procedures.extend(labtracks_surgeries)
            logging.info(
                f"Found {len(labtracks_surgeries)} surgeries "
                f"from LabTracks for {subject_id}"
            )

        if self.las_2020:
            las_2020_surgeries = (
                self.map_sharepoint_response_to_aind_surgeries(
                    response=self.las_2020,
                    mapper_cls=MappedLAS2020,
                    subject_id=subject_id,
                )
            )
            subject_procedures.extend(las_2020_surgeries)
            logging.info(
                f"Found {len(las_2020_surgeries)} surgeries "
                f"from LAS2020 for {subject_id}"
            )

        if not subject_procedures and not specimen_procedures:
            return None
        return Procedures(
            subject_id=subject_id,
            subject_procedures=subject_procedures,
            specimen_procedures=specimen_procedures,
        )
