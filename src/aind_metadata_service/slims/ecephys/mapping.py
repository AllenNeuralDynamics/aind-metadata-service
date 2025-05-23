"""
Module to handle mapping data from SLIMS
"""

import html
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, field_validator

from aind_metadata_service.slims.ecephys.handler import (
    SlimsEcephysData,
    SlimsRewardSpouts,
)


class StreamModule(BaseModel):
    """Stream Module"""

    implant_hole: Optional[Decimal] = None
    assembly_name: Optional[str] = None
    probe_name: Optional[str] = None
    primary_target_structure: Optional[str] = None
    secondary_target_structures: Optional[list] = None
    arc_angle: Optional[Decimal] = None
    module_angle: Optional[Decimal] = None
    rotation_angle: Optional[Decimal] = None
    coordinate_transform: Optional[str] = None
    ccf_coordinate_ap: Optional[Decimal] = None
    ccf_coordinate_ml: Optional[Decimal] = None
    ccf_coordinate_dv: Optional[Decimal] = None
    ccf_coordinate_unit: Optional[str] = None
    ccf_version: Optional[str] = None
    bregma_target_ap: Optional[Decimal] = None
    bregma_target_ml: Optional[Decimal] = None
    bregma_target_dv: Optional[Decimal] = None
    bregma_target_unit: Optional[str] = None
    surface_z: Optional[Decimal] = None
    surface_z_unit: Optional[str] = None
    manipulator_x: Optional[Decimal] = None
    manipulator_y: Optional[Decimal] = None
    manipulator_z: Optional[Decimal] = None
    manipulator_unit: Optional[str] = None
    dye: Optional[str] = None

    @field_validator(
        "ccf_coordinate_unit",
        "bregma_target_unit",
        "surface_z_unit",
        "manipulator_unit",
        mode="before",
    )
    def parse_micrometer_unit(cls, v):
        """Parse HTML entity for micrometer"""
        if isinstance(v, str):
            v = html.unescape(v)
        return v


class EcephysData(BaseModel):
    """Model for Ecephys data"""

    experiment_run_created_on: Optional[datetime] = None
    subject_id: Optional[str] = None
    operator: Optional[str] = None
    instrument: Optional[str] = None
    session_type: Optional[str] = None
    mouse_platform_name: Optional[str] = None
    active_mouse_platform: Optional[bool] = None
    session_name: Optional[str] = None
    animal_weight_prior: Optional[Decimal] = None
    animal_weight_after: Optional[Decimal] = None
    animal_weight_unit: Optional[str] = None
    reward_consumed: Optional[Decimal] = None
    reward_consumed_unit: Optional[str] = None
    link_to_stimulus_epoch_code: Optional[str] = None
    reward_solution: Optional[str] = None
    other_reward_solution: Optional[str] = None
    reward_spouts: Optional[List[SlimsRewardSpouts]] = []
    stream_modalities: Optional[List[str]] = None
    stream_modules: Optional[List[StreamModule]] = []
    daq_names: Optional[List[str]] = None
    camera_names: Optional[List[str]] = None


class SlimsEcephysMapper:
    """Class to handle mapping data from slims to a standard data model"""

    def __init__(self, slims_ephys_data: List[SlimsEcephysData]):
        """Class constructor"""
        self.slims_ephys_data = slims_ephys_data

    def map_info_from_slims(self) -> List[EcephysData]:
        """Maps info from slims into data model"""
        ephys_data = [
            EcephysData.model_validate(m.model_dump())
            for m in self.slims_ephys_data
        ]
        ephys_data.sort(
            key=lambda m: (
                m.experiment_run_created_on is None,
                m.experiment_run_created_on,
            ),
            reverse=True,
        )
        return ephys_data
