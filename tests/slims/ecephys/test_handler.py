"""Tests methods in ecephys handler module"""

import json
import os
import unittest
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

from slims.internal import Record

from aind_metadata_service.slims.ecephys.handler import (
    SlimsEcephysData,
    SlimsEcephysHandler,
    SlimsRewardSpouts,
    SlimsStreamModule,
)

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / ".."
    / "resources"
    / "slims"
    / "ecephys"
)


class TestSlimsEcephysHandler(unittest.TestCase):
    """Tests methods in SlimsEcephsHandler class"""

    @classmethod
    def setUp(cls):
        """Set up the test environment"""

        def form_record(json_entity: Dict[str, Any]) -> Record:
            """Build a record object"""
            # noinspection PyTypeChecker
            return Record(json_entity=json_entity, slims_api=None)

        with open(RESOURCES_DIR / "content.json", "r") as f:
            content_json = json.load(f)
        with open(RESOURCES_DIR / "experiment_run.json", "r") as f:
            experiment_run_json = json.load(f)
        with open(RESOURCES_DIR / "experiment_run_step.json", "r") as f:
            experiment_run_step_json = json.load(f)
        with open(
            RESOURCES_DIR / "experiment_run_step_content.json", "r"
        ) as f:
            experiment_run_step_content_json = json.load(f)
        with open(RESOURCES_DIR / "experiment_template.json", "r") as f:
            experiment_template_json = json.load(f)
        with open(RESOURCES_DIR / "reference_data_record.json", "r") as f:
            reference_data_record_json = json.load(f)
        with open(RESOURCES_DIR / "result.json", "r") as f:
            result_json = json.load(f)

        content = [form_record(j) for j in content_json]
        experiment_run = [form_record(j) for j in experiment_run_json]
        experiment_run_step = [
            form_record(j) for j in experiment_run_step_json
        ]
        experiment_run_step_content = [
            form_record(j) for j in experiment_run_step_content_json
        ]
        experiment_template = [
            form_record(j) for j in experiment_template_json
        ]
        reference_data_record = [
            form_record(j) for j in reference_data_record_json
        ]
        result = [form_record(j) for j in result_json]
        cls.fetch_side_effect = [
            experiment_template,
            experiment_run,
            experiment_run_step,
            experiment_run_step_content,
            result,
            content,
            reference_data_record,
            reference_data_record,
        ]

    @patch("slims.slims.Slims")
    def test_get_graph(self, mock_slims: MagicMock):
        """Tests _get_graph method"""

        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsEcephysHandler(client=mock_slims)
        G, root_nodes = handler._get_graph()
        expected_root_nodes = [
            "ExperimentRun.40007",
        ]
        expected_edges = [
            ("ExperimentRun.40007", "ExperimentRunStep.60027"),
            ("ExperimentRun.40007", "ExperimentRunStep.60028"),
            ("ExperimentRun.40007", "ExperimentRunStep.60029"),
            ("ExperimentRun.40007", "ExperimentRunStep.60030"),
            ("ExperimentRunStep.60027", "ExperimentRunStepContent.9"),
            ("ExperimentRunStep.60029", "Result.1581"),
            ("ExperimentRunStep.60030", "Result.1611"),
            ("ExperimentRunStepContent.9", "Content.166"),
            ("Result.1581", "ReferenceDataRecord.3466"),
            ("Result.1611", "ReferenceDataRecord.4512"),
            ("ReferenceDataRecord.3466", "ReferenceDataRecord.3467"),
        ]
        self.assertEqual(expected_root_nodes, root_nodes)
        self.assertCountEqual(expected_edges, G.edges())

    @patch("slims.slims.Slims")
    def test_parse_graph(self, mock_slims: MagicMock):
        """Tests _parse_graph method."""
        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsEcephysHandler(client=mock_slims)
        g, root_nodes = handler._get_graph()
        ecephys_data = handler._parse_graph(
            g=g, root_nodes=root_nodes, subject_id="750108", session_name=None
        )
        expected_ecephys_data = [
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
                animal_weight_prior=Decimal("30.2"),
                animal_weight_after=Decimal("30.5"),
                animal_weight_unit="g",
                reward_consumed=Decimal("1"),
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
                        arc_angle=Decimal("-17.0"),
                        module_angle=Decimal("12.0"),
                        rotation_angle=Decimal("0.0"),
                        coordinate_transform=(
                            "calibration_info_np2_2024_12_23T11_36_00.xlsx"
                        ),
                        ccf_coordinate_ap=Decimal("0.5"),
                        ccf_coordinate_ml=Decimal("0.5"),
                        ccf_coordinate_dv=Decimal("0.5"),
                        ccf_coordinate_unit="&mu;m",
                        ccf_version=None,
                        bregma_target_ap=Decimal("0.5"),
                        bregma_target_ml=Decimal("0.5"),
                        bregma_target_dv=Decimal("0.5"),
                        bregma_target_unit="mm",
                        surface_z=Decimal("5508.5"),
                        surface_z_unit="&mu;m",
                        manipulator_x=Decimal("7610.0"),
                        manipulator_y=Decimal("9063.0"),
                        manipulator_z=Decimal("6703.0"),
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
        self.assertEqual(expected_ecephys_data, ecephys_data)

    @patch("slims.slims.Slims")
    def test_get_ephys_data_from_slims(self, mock_slims: MagicMock):
        """Tests get_ephys_data_from_slims method"""
        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsEcephysHandler(client=mock_slims)
        ecephys_data = handler.get_ephys_data_from_slims(subject_id="750108")
        self.assertEqual(1, len(ecephys_data))

    @patch("slims.slims.Slims")
    def test_get_ephys_data_from_slims_error(self, mock_slims: MagicMock):
        """Tests get_ephys_data_from_slims method when subject_id empty"""
        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsEcephysHandler(client=mock_slims)
        with self.assertRaises(ValueError) as e:
            handler.get_ephys_data_from_slims(subject_id="")

        self.assertIn("subject_id must not be empty!", str(e.exception))


if __name__ == "__main__":
    unittest.main()
