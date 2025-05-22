"""Tests methods in handler module"""

import json
import os
import unittest
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

from slims.internal import Record

from aind_metadata_service.slims.viral_injection.handler import (
    SlimsViralInjectionData,
    SlimsViralInjectionHandler,
    SlimsViralMaterialData,
)

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / ".."
    / "resources"
    / "slims"
    / "viral_injection"
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

        with open(RESOURCES_DIR / "vi_content.json", "r") as f:
            vi_content_json = json.load(f)
        with open(RESOURCES_DIR / "vm_content.json", "r") as f:
            vm_content_json = json.load(f)
        with open(RESOURCES_DIR / "order.json", "r") as f:
            order_json = json.load(f)
        with open(RESOURCES_DIR / "content_relation.json", "r") as f:
            content_relation_json = json.load(f)
        with open(RESOURCES_DIR / "content_type.json", "r") as f:
            content_type_json = json.load(f)
        vi_content = [form_record(j) for j in vi_content_json]
        vm_content = [form_record(j) for j in vm_content_json]
        order = [form_record(j) for j in order_json]
        content_relation = [form_record(j) for j in content_relation_json]
        content_type = [form_record(j) for j in content_type_json]
        cls.fetch_side_effect = [
            content_type,
            vi_content,
            content_relation,
            vm_content,
            order,
        ]

    @patch("slims.slims.Slims")
    def test_get_graph(self, mock_slims: MagicMock):
        """Tests _get_graph method"""

        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsViralInjectionHandler(client=mock_slims)
        G, root_nodes = handler._get_graph()
        expected_root_nodes = ["Content.994"]
        expected_edges = [
            ("Content.994", "ContentRelation.202"),
            ("ContentRelation.202", "Content.992"),
            ("Content.994", "Order.124"),
        ]
        self.assertEqual(expected_root_nodes, root_nodes)
        self.assertCountEqual(expected_edges, G.edges())

    @patch("slims.slims.Slims")
    def test_parse_graph(self, mock_slims: MagicMock):
        """Tests _parse_graph method."""
        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsViralInjectionHandler(client=mock_slims)
        g, root_nodes = handler._get_graph()
        inj_data = handler._parse_graph(
            g=g, root_nodes=root_nodes, subject_id="614178"
        )
        expected_inj_data = [
            SlimsViralInjectionData(
                content_category="Viral Materials",
                content_type="Viral injection",
                content_created_on=None,
                content_modified_on=None,
                name="INJ00000002",
                viral_injection_buffer="AAV Buffer",
                volume=Decimal(str(98.56)),
                volume_unit="&mu;l",
                labeling_protein="tdTomato",
                date_made=1746014400000,
                intake_date=None,
                storage_temperature="4 C",
                special_storage_guidelines=["Light sensitive storage"],
                special_handling_guidelines=["BSL - 1"],
                mix_count=None,
                derivation_count=None,
                ingredient_count=None,
                assigned_mice=["614178"],
                requested_for_date=None,
                planned_injection_date=1746705600000,
                planned_injection_time=None,
                order_created_on=1746717795853,
                viral_materials=[
                    SlimsViralMaterialData(
                        content_category="Viral Materials",
                        content_type="Viral solution",
                        content_created_on=1746049926016,
                        content_modified_on=None,
                        viral_solution_type="Injection Dilution",
                        virus_name="7x-TRE-tDTomato",
                        lot_number="VT5355g",
                        lab_team="Molecular Anatomy",
                        virus_type="AAV",
                        virus_serotype="PhP.eB",
                        virus_plasmid_number="AiP300001",
                        name="VRS00000029",
                        dose=Decimal(str(180000000000)),
                        dose_unit=None,
                        titer=Decimal(str(24200000000000)),
                        titer_unit="GC/ml",
                        volume=Decimal(str(8.55)),
                        volume_unit="&mu;l",
                        date_made=1746049926079,
                        intake_date=None,
                        storage_temperature="-80 C",
                        special_storage_guidelines=[
                            "Avoid freeze - thaw cycles"
                        ],
                        special_handling_guidelines=["BSL - 1"],
                        parent_name=None,
                        mix_count=1,
                        derivation_count=0,
                        ingredient_count=0,
                    )
                ],
            )
        ]
        self.assertEqual(expected_inj_data, inj_data)

    @patch("slims.slims.Slims")
    def test_get_viral_injection_data_from_slims(self, mock_slims: MagicMock):
        """Tests get_viral_injection_info_from_slims method"""
        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsViralInjectionHandler(client=mock_slims)
        spim_data = handler.get_viral_injection_info_from_slims(
            subject_id="614178"
        )
        self.assertEqual(1, len(spim_data))

    @patch("slims.slims.Slims")
    def test_get_viral_injection_info_from_slims_error(
        self, mock_slims: MagicMock
    ):
        """Tests get_viral_injection_info_from_slims when subject_id empty"""
        mock_slims.fetch.side_effect = self.fetch_side_effect
        handler = SlimsViralInjectionHandler(client=mock_slims)
        with self.assertRaises(ValueError) as e:
            handler.get_viral_injection_info_from_slims(subject_id="")

        self.assertIn("subject_id must not be empty!", str(e.exception))


if __name__ == "__main__":
    unittest.main()
