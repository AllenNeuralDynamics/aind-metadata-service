"""Tests methods in handler module"""

import json
import os
import unittest
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

from slims.internal import Record

from aind_metadata_service.slims.histology.handler import (
    SlimsHistologyData,
    SlimsHistologyHandler,
    SlimsReagentData,
    SlimsWashData,
)

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / ".."
    / "resources"
    / "slims"
    / "histology"
)


class TestSlimsHistologyHandler(unittest.TestCase):
    """Tests methods in SlimsImagingHandler class"""

    @classmethod
    def setUp(cls):
        """Set up the test environment"""

        def form_record(json_entity: Dict[str, Any]) -> Record:
            """Build a record object"""
            # noinspection PyTypeChecker
            return Record(json_entity=json_entity, slims_api=None)

        with open(RESOURCES_DIR / "reagent_content.json", "r") as f:
            reagent_content_json = json.load(f)
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
        with open(RESOURCES_DIR / "sop.json", "r") as f:
            sop_json = json.load(f)

        content = [form_record(j) for j in content_json]
        reagent_content = [form_record(j) for j in reagent_content_json]
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
        sop = [form_record(j) for j in sop_json]
        cls.reagent_content = reagent_content
        cls.fetch_side_effect = [
            experiment_template,
            experiment_run,
            experiment_run_step,
            sop,
            experiment_run_step_content,
            content,
            reagent_content,
            reference_data_record,
        ]

    def test_get_reagent_data(self):
        """Tests _get_reagent_data"""
        records = self.reagent_content
        reagent_data = SlimsHistologyHandler._get_reagent_data(records)
        expected_data = [
            SlimsReagentData(
                name="112372-100G", source=None, lot_number="stbk5149"
            )
        ]
        self.assertEqual(expected_data, reagent_data)

    @patch("slims.slims.Slims")
    def test_get_specimen_data(self, mock_slims: MagicMock):
        """Tests _get_specimen_data"""
        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsHistologyHandler(client=mock_slims)
        G, _ = handler._get_graph()
        exp_run_step_content = "ExperimentRunStepContent.9"
        subject_id, specimen_id = handler._get_specimen_data(
            g=G, exp_run_step_content=exp_run_step_content
        )
        self.assertEqual("BRN00000002", specimen_id)
        self.assertEqual("754372", subject_id)

    @patch("slims.slims.Slims")
    def test_get_wash_data(self, mock_slims: MagicMock):
        """Tests _get_wash_data"""
        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsHistologyHandler(client=mock_slims)
        G, _ = handler._get_graph()
        exp_run_step = "ExperimentRunStep.60029"
        row = G.nodes[exp_run_step]["row"]
        wash_data = handler._get_wash_data(
            g=G, exp_run_step=exp_run_step, exp_run_step_row=row
        )
        expected_wash_data = SlimsWashData(
            wash_name="Refractive Index Matching Wash",
            wash_type="Refractive Index Matching",
            start_time=1737744000000,
            end_time=1738003200000,
            modified_by="PersonM",
            reagents=[
                SlimsReagentData(
                    name="112372-100G", source=None, lot_number="stbk5149"
                )
            ],
        )
        self.assertEqual(expected_wash_data, wash_data)

    @patch("slims.slims.Slims")
    def test_get_graph(self, mock_slims: MagicMock):
        """Tests _get_graph method"""

        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsHistologyHandler(client=mock_slims)
        G, root_nodes = handler._get_graph()
        expected_nodes = [
            "ExperimentRun.40007",
            "ExperimentRunStep.60027",
            "ExperimentRunStep.60028",
            "ExperimentRunStep.60029",
            "ExperimentRunStep.60030",
            "ExperimentRunStep.60031",
            "SOP.24",
            "ExperimentRunStepContent.9",
            "Content.166",
            "Content.138",
            "ReferenceDataRecord.1664",
        ]
        expected_edges = [
            ("ExperimentRun.40007", "ExperimentRunStep.60027"),
            ("ExperimentRun.40007", "ExperimentRunStep.60028"),
            ("ExperimentRun.40007", "ExperimentRunStep.60029"),
            ("ExperimentRun.40007", "ExperimentRunStep.60030"),
            ("ExperimentRun.40007", "ExperimentRunStep.60031"),
            ("ExperimentRunStep.60027", "ExperimentRunStepContent.9"),
            ("ExperimentRunStep.60028", "SOP.24"),
            ("ExperimentRunStep.60029", "Content.138"),
            ("ExperimentRunStepContent.9", "Content.166"),
            ("Content.138", "ReferenceDataRecord.1664"),
        ]
        self.assertCountEqual(expected_nodes, G.nodes)
        self.assertCountEqual(expected_edges, G.edges)

    @patch("slims.slims.Slims")
    def test_parse_graph(self, mock_slims: MagicMock):
        """Tests _parse_graph_method"""

        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsHistologyHandler(client=mock_slims)
        G, root_nodes = handler._get_graph()

        hist_data = handler._parse_graph(
            g=G, root_nodes=root_nodes, subject_id=None
        )
        expected_hist_data = [
            SlimsHistologyData(
                procedure_name="SmartSPIM Refractive Index Matching",
                experiment_run_created_on=1738175075574,
                specimen_id="BRN00000002",
                subject_id="754372",
                protocol_id=(
                    '<a href="https://www.protocols.io/edit/'
                    'refractive-index-matching-ethyl-cinnamate-cukpwuvn" '
                    'target="_blank" '
                    'rel="nofollow noopener noreferrer">'
                    "Refractive Index Matching - Ethyl Cinnamate</a>"
                ),
                protocol_name=(
                    "Refractive Index Matching - Ethyl Cinnamate (UNPUBLISHED)"
                ),
                washes=[
                    SlimsWashData(
                        wash_name="Refractive Index Matching Wash",
                        wash_type="Refractive Index Matching",
                        start_time=1737744000000,
                        end_time=1738003200000,
                        modified_by="PersonM",
                        reagents=[
                            SlimsReagentData(
                                name="112372-100G",
                                source=None,
                                lot_number="stbk5149",
                            )
                        ],
                    )
                ],
            )
        ]
        self.assertEqual(expected_hist_data, hist_data)

    @patch("slims.slims.Slims")
    def test_get_hist_data_from_slims(self, mock_slims: MagicMock):
        """Tests get_hist_data_from_slims method"""

        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsHistologyHandler(client=mock_slims)
        hist_data = handler.get_hist_data_from_slims(subject_id=None)
        self.assertEqual(1, len(hist_data))

    @patch("slims.slims.Slims")
    def test_get_hist_data_from_slims_error(self, mock_slims: MagicMock):
        """Tests get_hist_data_from_slims method"""

        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsHistologyHandler(client=mock_slims)
        with self.assertRaises(ValueError) as e:
            handler.get_hist_data_from_slims(subject_id="")
        self.assertIn("subject_id must not be empty!", str(e.exception))


if __name__ == "__main__":
    unittest.main()
