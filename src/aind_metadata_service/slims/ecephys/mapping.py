"""
Module to handle mapping data from SLIMS
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, field_validator

from aind_metadata_service.slims.ecephys.handler import SlimsEcephysData, SlimsRewardSpouts

class StreamModule(BaseModel):
    """Stream Module"""
    
    implant_hole: Optional[float] = None
    assembly_name: Optional[str] = None
    probe_name: Optional[str] = None
    primary_target_structure: Optional[str] = None
    secondary_target_structures: Optional[str] = None
    arc_angle: Optional[float] = None
    module_angle: Optional[float] = None
    rotation_angle: Optional[float] = None
    angle_unit: Optional[str] = None
    coordinate_transform: Optional[str] = None
    ccf_coordinate_ap: Optional[float] = None
    ccf_coordinate_ml: Optional[float] = None
    ccf_coordinate_dv: Optional[float] = None
    ccf_coordinate_unit: Optional[str] = None
    ccf_version: Optional[str] = None
    bregma_target_ap: Optional[float] = None
    bregma_target_ml: Optional[float] = None
    bregma_target_dv: Optional[float] = None
    bregma_target_unit: Optional[str] = None
    surface_z: Optional[float] = None
    surface_z_unit: Optional[str] = None
    manipulator_x: Optional[float] = None
    manipulator_y: Optional[float] = None
    manipulator_z: Optional[float] = None
    manipulator_unit: Optional[str] = None
    dye: Optional[str] = None

    @field_validator("ccf_coordinate_unit", "bregma_target_unit", "surface_z_unit", "manipulator_unit", mode="before")
    def parse_micrometer_unit(cls, v):
        """Parse HTML entity for micrometer"""
        if isinstance(v, str) and v.strip() == "&mu;m":
            return "um"
        return v
class EcephysData(BaseModel):
    """Model for Ecephys data"""

    experiment_run_created_on: Optional[int] = None
    subject_id: Optional[str] = None
    operator: Optional[str] = None
    instrument: Optional[str] = None
    session_type: Optional[str] = None
    # device_calibrations: Optional[str] = None attachment
    mouse_platform_name: Optional[str] = None
    active_mouse_platform: Optional[bool] = None
    session_name: Optional[str] = None
    animal_weight_prior: Optional[float] = None
    animal_weight_after: Optional[float] = None
    animal_weight_unit: Optional[str] = None
    reward_consumed: Optional[float] = None
    reward_consumed_unit: Optional[str] = None
    # stimulus_epochs: Optional[str] = None # attachment
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