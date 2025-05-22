"""Tests methods in handler module"""

import json
import os
import unittest
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

from slims.internal import Record

from aind_metadata_service.slims.imaging.handler import (
    SlimsImagingHandler,
    SlimsSpimData,
)

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / ".."
    / "resources"
    / "slims"
    / "imaging"
)


class TestSlimsImagingHandler(unittest.TestCase):
    """Tests methods in SlimsImagingHandler class"""

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
        with open(RESOURCES_DIR / "sop.json", "r") as f:
            sop_json = json.load(f)
        with open(RESOURCES_DIR / "order_content.json", "r") as f:
            order_content_json = json.load(f)
        with open(RESOURCES_DIR / "order.json", "r") as f:
            order_json = json.load(f)

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
        sop = [form_record(j) for j in sop_json]
        order_content = [form_record(j) for j in order_content_json]
        order = [form_record(j) for j in order_json]
        cls.fetch_side_effect = [
            experiment_template,
            experiment_run,
            experiment_run_step,
            sop,
            experiment_run_step_content,
            result,
            content,
            reference_data_record,
            order_content,
            order,
        ]

    @patch("slims.slims.Slims")
    def test_get_graph(self, mock_slims: MagicMock):
        """Tests _get_graph method"""

        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsImagingHandler(client=mock_slims)
        G, root_nodes = handler._get_graph()
        expected_root_nodes = [
            "ExperimentRun.40015",
            "ExperimentRun.40016",
            "ExperimentRun.40017",
        ]
        expected_edges = [
            ("ExperimentRun.40015", "ExperimentRunStep.60059"),
            ("ExperimentRun.40015", "ExperimentRunStep.60060"),
            ("ExperimentRun.40015", "ExperimentRunStep.60061"),
            ("ExperimentRun.40016", "ExperimentRunStep.60062"),
            ("ExperimentRun.40016", "ExperimentRunStep.60063"),
            ("ExperimentRun.40016", "ExperimentRunStep.60064"),
            ("ExperimentRun.40017", "ExperimentRunStep.60065"),
            ("ExperimentRun.40017", "ExperimentRunStep.60066"),
            ("ExperimentRun.40017", "ExperimentRunStep.60067"),
            ("ExperimentRunStep.60059", "ExperimentRunStepContent.29"),
            ("ExperimentRunStep.60060", "Result.1581"),
            ("ExperimentRunStep.60061", "SOP.18"),
            ("ExperimentRunStep.60062", "ExperimentRunStepContent.30"),
            ("ExperimentRunStep.60063", "Result.1611"),
            ("ExperimentRunStep.60064", "SOP.18"),
            ("ExperimentRunStep.60065", "ExperimentRunStepContent.31"),
            ("ExperimentRunStep.60066", "Result.1644"),
            ("ExperimentRunStep.60067", "SOP.18"),
            ("ExperimentRunStepContent.29", "Content.233"),
            ("ExperimentRunStepContent.30", "Content.235"),
            ("ExperimentRunStepContent.31", "Content.234"),
            ("Result.1581", "ReferenceDataRecord.40"),
            ("Result.1581", "ReferenceDataRecord.1624"),
            ("Result.1611", "ReferenceDataRecord.40"),
            ("Result.1611", "ReferenceDataRecord.1624"),
            ("Result.1644", "ReferenceDataRecord.40"),
            ("Result.1644", "ReferenceDataRecord.1624"),
            ("Content.235", "OrderContent.32"),
            ("OrderContent.32", "Order.21"),
        ]

        self.assertEqual(expected_root_nodes, root_nodes)
        self.assertCountEqual(expected_edges, G.edges())

    @patch("slims.slims.Slims")
    def test_parse_graph(self, mock_slims: MagicMock):
        """Tests _parse_graph method."""
        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsImagingHandler(client=mock_slims)
        g, root_nodes = handler._get_graph()
        spim_data = handler._parse_graph(
            g=g, root_nodes=root_nodes, subject_id="744742"
        )
        expected_spim_data = [
            SlimsSpimData(
                experiment_run_created_on=1739383241200,
                specimen_id="BRN00000018",
                subject_id="744742",
                protocol_name="Imaging cleared mouse brains on SmartSPIM",
                protocol_id=(
                    "<a href="
                    '"https://dx.doi.org/10.17504/protocols.io.3byl4jo1rlo5/'
                    'v1" '
                    'target="_blank" '
                    'rel="nofollow noopener noreferrer">'
                    "Imaging cleared mouse brains on SmartSPIM"
                    "</a>"
                ),
                date_performed=1739383260000,
                chamber_immersion_medium="Ethyl Cinnamate",
                sample_immersion_medium="Ethyl Cinnamate",
                chamber_refractive_index=Decimal(str(1.557)),
                sample_refractive_index=Decimal(str(1.557)),
                instrument_id="440_SmartSPIM1_20240327",
                experimenter_name="Person R",
                z_direction="Superior to Inferior",
                y_direction="Anterior to Posterior",
                x_direction="Left to Right",
                imaging_channels=[
                    "Laser = 488; Emission Filter = 525/45",
                    "Laser = 561; Emission Filter = 593/40",
                    "Laser = 639; Emission Filter = 667/30",
                ],
                stitching_channels="Laser = 639, Emission Filter = 667/30",
                ccf_registration_channels=(
                    "Laser = 639, Emission Filter = 667/30"
                ),
                cell_segmentation_channels=None,
            )
        ]
        self.assertEqual(expected_spim_data, spim_data)

    @patch("slims.slims.Slims")
    def test_get_spim_data_from_slims(self, mock_slims: MagicMock):
        """Tests get_spim_data_from_slims method"""
        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsImagingHandler(client=mock_slims)
        spim_data = handler.get_spim_data_from_slims(subject_id="744742")
        self.assertEqual(1, len(spim_data))

    @patch("slims.slims.Slims")
    def test_get_spim_data_from_slims_error(self, mock_slims: MagicMock):
        """Tests get_spim_data_from_slims method when subject_id empty"""
        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsImagingHandler(client=mock_slims)
        with self.assertRaises(ValueError) as e:
            handler.get_spim_data_from_slims(subject_id="")

        self.assertIn("subject_id must not be empty!", str(e.exception))


if __name__ == "__main__":
    unittest.main()
