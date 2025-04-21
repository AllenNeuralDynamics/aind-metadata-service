"""
Module to handle mapping data from SLIMS
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, field_validator

from aind_metadata_service.slims.imaging.handler import SlimsSpimData
from aind_metadata_service.slims.table_handler import parse_html


class SpimData(BaseModel):
    """Model for SPIM Imaging data"""

    experiment_run_created_on: Optional[datetime] = None
    specimen_id: Optional[str] = None
    subject_id: Optional[str] = None
    protocol_name: Optional[str] = None
    protocol_id: Optional[str] = None
    date_performed: Optional[datetime] = None
    chamber_immersion_medium: Optional[str] = None
    sample_immersion_medium: Optional[str] = None
    chamber_refractive_index: Optional[Decimal] = None
    sample_refractive_index: Optional[Decimal] = None
    instrument_id: Optional[str] = None
    experimenter_name: Optional[str] = None
    z_direction: Optional[str] = None
    y_direction: Optional[str] = None
    x_direction: Optional[str] = None
    imaging_channels: Optional[List[str]] = []
    stitching_channels: Optional[str] = None
    ccf_registration_channels: Optional[str] = None
    cell_segmentation_channels: Optional[List[str]] = []

    @field_validator("protocol_id")
    def parse_protocol_id(cls, v: Optional[str]) -> Optional[str]:
        """Parse link from html tag"""
        return parse_html(v)


class SlimsSpimMapper:
    """Class to handle mapping data from slims to a standard data model"""

    def __init__(self, slims_spim_data: List[SlimsSpimData]):
        """Class constructor"""
        self.slims_spim_data = slims_spim_data

    def map_info_from_slims(self) -> List[SpimData]:
        """Maps info from slims into data model"""
        spim_data = [
            SpimData.model_validate(m.model_dump())
            for m in self.slims_spim_data
        ]
        spim_data.sort(
            key=lambda m: (
                m.experiment_run_created_on is None,
                m.experiment_run_created_on,
            ),
            reverse=True,
        )
        return spim_data
