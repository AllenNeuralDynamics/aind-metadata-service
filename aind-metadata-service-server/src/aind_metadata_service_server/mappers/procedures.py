"""Maps information to aind-data-schema Procedures model."""

import re
from decimal import Decimal
from typing import List, Optional, Union
from pydantic import ValidationError
from aind_labtracks_service_async_client.models import (
    Task as LabTracksTask,
)
from aind_sharepoint_service_async_client.models import (
    NSB2019List,
    NSB2023List,
    Las2020List,
)
from aind_data_schema.core.procedures import (
    Procedures,
    Surgery,
    Perfusion,
    RetroOrbitalInjection,
)
from enum import Enum
import logging
from aind_metadata_service_server.mappers.nsb2019 import MappedNSBList as MappedNSB2019
from aind_metadata_service_server.mappers.nsb2023 import MappedNSBList as MappedNSB2023
from aind_metadata_service_server.mappers.las2020 import MappedLASList as MappedLAS2020

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

class ProceduresMapper:
    """Class to handle mapping of data."""

    def __init__(
        self,
        labtracks_tasks: List[LabTracksTask] = None,
        nsb_2019: List[NSB2019List] = None,
        nsb_2023: List[NSB2023List] = None,
        nsb_present: List[NSB2023List] = None,
        las_2020: List[Las2020List] = None
    ):
        """
        Class constructor.
        Parameters
        ----------
        labtracks_tasks :  List[LabTracksTask]
        """
        self.labtracks_tasks = labtracks_tasks
        self.nsb_2019 = nsb_2019
        self.nsb_2023 = nsb_2023
        self.nsb_present = nsb_present
        self.las_2020 = las_2020

    def _map_labtracks_task_to_aind_surgery(self, task: LabTracksTask) -> Union[Surgery, None]:
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
        
        experimenter_full_name = str(task.investigator_id) if task.investigator_id else None
        iacuc_protocol = str(task.protocol_number) if task.protocol_number else None
        type_name = task.type_name
        task_status = task.task_status
        
        if not (type_name and task_status == LabTracksTaskStatuses.FINISHED.value):
            return None
        
        if LabTracksProcedures.PERFUSION.value.lower() in type_name.lower():
            output_specimen_ids = {
                str(task.task_object)
            } if task.task_object else set()
            
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
        
        elif LabTracksProcedures.RO_INJECTION.value in type_name.lower():
            return Surgery.model_construct(
                start_date=start_date,
                experimenter_full_name=experimenter_full_name,
                iacuc_protocol=iacuc_protocol,
                animal_weight_prior=None,
                animal_weight_post=None,
                anaesthesia=None,
                notes=None,
                procedures=[
                    RetroOrbitalInjection.model_construct(
                        injection_volume=None, 
                        injection_eye=None
                    )
                ],
            )
        
        return None

    def map_labtracks_response_to_aind_surgeries(self) -> List[Surgery]:
        """
        Maps the instance's LabTracks tasks to a list of Surgery objects using the helper method.
        
        Returns
        -------
        List[Surgery]
            A list of mapped Surgery objects (not validated)
        """
        surgeries_list = []
        
        for task in self.labtracks_tasks:
            surgery = self._map_labtracks_task_to_aind_surgery(task)
            if surgery:
                surgeries_list.append(surgery)
        
        return surgeries_list
    
    @staticmethod
    def map_sharepoint_response_to_aind_surgeries(response: List, mapper_cls: type, subject_id: Optional[str] = None) -> List[Surgery]:
        """
        Generic method to map SharePoint data to Surgery objects using the provided mapper class.
        
        Parameters
        ----------
        response : List
            List of SharePoint model objects to map
        mapper_cls : Type
            The mapper class to use for mapping (e.g., MappedNSB2019, MappedNSB2023, MappedLAS2020)
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
    
    def map_responses_to_aind_procedures(self, subject_id: str) -> Union[Procedures, None]:
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
        all_surgeries = []
        if self.labtracks_tasks:
            labtracks_surgeries = self.map_labtracks_response_to_aind_surgeries()
            all_surgeries.extend(labtracks_surgeries)
            logging.info(f"Found {len(labtracks_surgeries)} surgeries from LabTracks for {subject_id}")

        if self.nsb_2019:
            nsb_2019_surgeries = self.map_sharepoint_response_to_aind_surgeries(
                response=self.nsb_2019,
                mapper_cls=MappedNSB2019,
            )
            all_surgeries.extend(nsb_2019_surgeries)
            logging.info(f"Found {len(nsb_2019_surgeries)} surgeries from NSB2019 for {subject_id}")

        if self.nsb_2023:
            nsb_2023_surgeries = self.map_sharepoint_response_to_aind_surgeries(
                response=self.nsb_2023,
                mapper_cls=MappedNSB2023,
            )
            all_surgeries.extend(nsb_2023_surgeries)
            logging.info(f"Found {len(nsb_2023_surgeries)} surgeries from NSB2023 for {subject_id}")

        if self.nsb_present:
            nsb_present_surgeries = self.map_sharepoint_response_to_aind_surgeries(
                response=self.nsb_present,
                mapper_cls=MappedNSB2023,
            )
            all_surgeries.extend(nsb_present_surgeries)
            logging.info(f"Found {len(nsb_present_surgeries)} surgeries from NSB Present for {subject_id}")

        if self.las_2020:
            las_2020_surgeries = self.map_sharepoint_response_to_aind_surgeries(
                response=self.las_2020,
                mapper_cls=MappedLAS2020,
                subject_id=subject_id
            )
            all_surgeries.extend(las_2020_surgeries)
            logging.info(f"Found {len(las_2020_surgeries)} surgeries from LAS2020 for {subject_id}")
        
        if not all_surgeries:
            return None
        return Procedures(
            subject_id=subject_id,
            subject_procedures=all_surgeries
        )


