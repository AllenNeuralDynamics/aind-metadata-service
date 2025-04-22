"""Tests methods in handler module"""

import json
import os
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

from slims.internal import Record

from aind_metadata_service.slims.water_restriction.handler import (
    SlimsWaterRestrictionData,
    SlimsWaterRestrictionHandler,
)

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / ".."
    / "resources"
    / "slims"
    / "water_restriction"
)


class TestSlimsWaterRestrictionHandler(unittest.TestCase):
    """Tests methods in SlimsWaterRestriction class"""

    @classmethod
    def setUp(cls):
        """Set up the test environment"""

        def form_record(json_entity: Dict[str, Any]) -> Record:
            """Build a record object"""
            # noinspection PyTypeChecker
            return Record(json_entity=json_entity, slims_api=None)

        with open(RESOURCES_DIR / "content.json", "r") as f:
            content_json = json.load(f)
        with open(RESOURCES_DIR / "content_event.json", "r") as f:
            content_event_json = json.load(f)

        content = [form_record(j) for j in content_json]
        content_event = [form_record(j) for j in content_event_json]
        cls.fetch_side_effect = [
            content_event,
            content,
        ]

    @patch("slims.slims.Slims")
    def test_get_graph(self, mock_slims: MagicMock):
        """Tests _get_graph method"""

        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsWaterRestrictionHandler(client=mock_slims)
        G, root_nodes = handler._get_graph()
        expected_root_nodes = ["ContentEvent.15"]
        expected_edges = [("ContentEvent.15", "Content.55")]
        self.assertEqual(expected_root_nodes, root_nodes)
        self.assertCountEqual(expected_edges, G.edges())

    @patch("slims.slims.Slims")
    def test_get_graph_date_criteria(self, mock_slims: MagicMock):
        """Tests _get_graph method"""

        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsWaterRestrictionHandler(client=mock_slims)
        G, root_nodes = handler._get_graph(
            start_date_greater_than_or_equal=datetime(2024, 12, 13, 19, 43, 32)
        )
        expected_root_nodes = ["ContentEvent.15"]
        expected_edges = [("ContentEvent.15", "Content.55")]
        self.assertEqual(expected_root_nodes, root_nodes)
        self.assertCountEqual(expected_edges, G.edges())

    @patch("slims.slims.Slims")
    def test_parse_graph(self, mock_slims: MagicMock):
        """Tests _parse_graph method."""
        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsWaterRestrictionHandler(client=mock_slims)
        g, root_nodes = handler._get_graph()
        wr_data = handler._parse_graph(
            g=g, root_nodes=root_nodes, subject_id="762287"
        )
        expected_wr_data = [
            SlimsWaterRestrictionData(
                content_event_created_on=1734119014103,
                subject_id="762287",
                start_date=1734119012354,
                end_date=None,
                assigned_by="person.name",
                target_weight_fraction=Decimal("0.85"),
                baseline_weight=Decimal("28.23"),
                weight_unit="g",
            )
        ]
        self.assertEqual(expected_wr_data, wr_data)

    @patch("slims.slims.Slims")
    def test_get_spim_data_from_slims(self, mock_slims: MagicMock):
        """Tests get_spim_data_from_slims method"""
        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsWaterRestrictionHandler(client=mock_slims)
        wr_data = handler.get_water_restriction_data_from_slims(
            subject_id="762287"
        )
        self.assertEqual(1, len(wr_data))

    @patch("slims.slims.Slims")
    def test_get_spim_data_from_slims_error(self, mock_slims: MagicMock):
        """Tests get_spim_data_from_slims method when subject_id empty"""
        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsWaterRestrictionHandler(client=mock_slims)
        with self.assertRaises(ValueError) as e:
            handler.get_water_restriction_data_from_slims(subject_id="")

        self.assertIn("subject_id must not be empty!", str(e.exception))


if __name__ == "__main__":
    unittest.main()
