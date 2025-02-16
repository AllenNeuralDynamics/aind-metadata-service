"""
Module to handle mapping data from SLIMS
"""

import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, field_validator

from aind_metadata_service.slims.imaging.handler import SlimsSpimData


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

    @field_validator("protocol_id")
    def parse_html(cls, v: Optional[str]) -> Optional[str]:
        """Parse link from html tag"""
        if v is None:
            return None
        try:
            root = ET.fromstring(v)
            return root.get("href")
        except ET.ParseError:
            return v
        except Exception as e:
            logging.warning(f"An exception occurred parsing link {v}: {e}")
            return None


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
