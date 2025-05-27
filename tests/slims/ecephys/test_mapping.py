"""Tests methods in mapping module"""

import os
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from aind_metadata_service.slims.ecephys.handler import (
    SlimsEcephysData,
    SlimsRewardSpouts,
    SlimsStreamModule,
)
from aind_metadata_service.slims.ecephys.mapping import (
    EcephysData,
    SlimsEcephysMapper,
    StreamModule,
)

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / ".."
    / "resources"
    / "slims"
    / "ecephys"
)


class TestSlimsSpimMapper(unittest.TestCase):
    """Tests methods in SlimsSpimMapper class"""

    def test_map_info_from_slims(self):
        """Tests map_info_from_slims method."""
        slims_ecephys_data = [
            SlimsEcephysData(
                experiment_run_created_on=1738175075574,
                subject_id="750108",
                operator="Person Merson",
                instrument=None,
                session_type="Dynamic Foraging",
                device_calibrations=None,
                mouse_platform_name="Dynamic Foraging",
                active_mouse_platform=True,
                session_name="ecephys_750108_2024-12-23_14-51-45",
                animal_weight_prior=30,
                animal_weight_after=30,
                animal_weight_unit="g",
                reward_consumed=1,
                reward_consumed_unit="ml",
                stimulus_epochs=410,
                link_to_stimulus_epoch_code=("git@github.com:SomeLink.git"),
                reward_solution="Water",
                other_reward_solution=None,
                reward_spouts=[
                    SlimsRewardSpouts(
                        spout_side="Water",
                        starting_position=None,
                        variable_position=None,
                    )
                ],
                stream_modalities=["Behavior", "Behavior Videos", "Ecephys"],
                stream_modules=[
                    SlimsStreamModule(
                        implant_hole=5,
                        assembly_name="50209",
                        probe_name="50209",
                        primary_target_structure="Retrosplenial area",
                        secondary_target_structures=None,
                        arc_angle=-17.0,
                        module_angle=12.0,
                        rotation_angle=0.0,
                        coordinate_transform=(
                            "calibration_info_np2_2024_12_23T11_36_00.xlsx"
                        ),
                        ccf_coordinate_ap=0.5,
                        ccf_coordinate_ml=0.5,
                        ccf_coordinate_dv=0.5,
                        ccf_coordinate_unit="&mu;m",
                        ccf_version=None,
                        bregma_target_ap=0.5,
                        bregma_target_ml=0.5,
                        bregma_target_dv=0.5,
                        bregma_target_unit="mm",
                        surface_z=None,
                        surface_z_unit=None,
                        manipulator_x=7610.0,
                        manipulator_y=9063.0,
                        manipulator_z=6703.0,
                        manipulator_unit="&mu;m",
                        dye="DiI",
                    )
                ],
                daq_names=["Basestation Slot 3"],
                camera_names=[
                    "Bottom camera",
                    "Eye camera",
                    "Side camera left",
                ],
            )
        ]
        mapper = SlimsEcephysMapper(slims_ephys_data=slims_ecephys_data)
        output = mapper.map_info_from_slims()
        expected_output = [
            EcephysData(
                experiment_run_created_on=datetime(
                    2025, 1, 29, 18, 24, 35, 574000, tzinfo=timezone.utc
                ),
                subject_id="750108",
                operator="Person Merson",
                instrument=None,
                session_type="Dynamic Foraging",
                mouse_platform_name="Dynamic Foraging",
                active_mouse_platform=True,
                session_name="ecephys_750108_2024-12-23_14-51-45",
                animal_weight_prior=Decimal("30.0"),
                animal_weight_after=Decimal("30.0"),
                animal_weight_unit="g",
                reward_consumed=Decimal("1.0"),
                reward_consumed_unit="ml",
                link_to_stimulus_epoch_code=("git@github.com:SomeLink.git"),
                reward_solution="Water",
                other_reward_solution=None,
                reward_spouts=[
                    SlimsRewardSpouts(
                        spout_side="Water",
                        starting_position=None,
                        variable_position=None,
                    )
                ],
                stream_modalities=["Behavior", "Behavior Videos", "Ecephys"],
                stream_modules=[
                    StreamModule(
                        implant_hole=5,
                        assembly_name="50209",
                        probe_name="50209",
                        primary_target_structure="Retrosplenial area",
                        secondary_target_structures=None,
                        arc_angle=Decimal("-17.0"),
                        module_angle=Decimal("12.0"),
                        rotation_angle=Decimal("0.0"),
                        coordinate_transform=(
                            "calibration_info_np2_2024_12_23T11_36_00.xlsx"
                        ),
                        ccf_coordinate_ap=Decimal("0.5"),
                        ccf_coordinate_ml=Decimal("0.5"),
                        ccf_coordinate_dv=Decimal("0.5"),
                        ccf_coordinate_unit="μm",
                        ccf_version=None,
                        bregma_target_ap=Decimal("0.5"),
                        bregma_target_ml=Decimal("0.5"),
                        bregma_target_dv=Decimal("0.5"),
                        bregma_target_unit="mm",
                        surface_z=None,
                        surface_z_unit=None,
                        manipulator_x=Decimal("7610.0"),
                        manipulator_y=Decimal("9063.0"),
                        manipulator_z=Decimal("6703.0"),
                        manipulator_unit="μm",
                        dye="DiI",
                    )
                ],
                daq_names=["Basestation Slot 3"],
                camera_names=[
                    "Bottom camera",
                    "Eye camera",
                    "Side camera left",
                ],
            )
        ]
        self.assertEqual(expected_output, output)


if __name__ == "__main__":
    unittest.main()
