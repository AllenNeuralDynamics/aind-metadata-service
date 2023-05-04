"""Tests NSB 2023 data model is parsed correctly"""

import json
import logging
import os
from copy import deepcopy
from pathlib import Path
from typing import List, Tuple
from unittest import TestCase
from unittest import main as unittest_main

from aind_data_schema.procedures import CraniotomyType, InjectionMaterial

from aind_metadata_service.sharepoint.nsb2023.mapping import NSB2023Mapping
from aind_metadata_service.sharepoint.nsb2023.models import NSBList2023

if os.getenv("LOG_LEVEL"):  # pragma: no cover
    logging.basicConfig(level=os.getenv("LOG_LEVEL"))

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".."
DIR_RAW = TEST_DIR / "resources" / "sharepoint" / "nsb2023" / "raw"
DIR_MAP = TEST_DIR / "resources" / "sharepoint" / "nsb2023" / "mapped"
LIST_ITEM_FILE_NAMES = os.listdir(DIR_RAW)
sorted(LIST_ITEM_FILE_NAMES)
LIST_ITEM_FILE_PATHS = [DIR_RAW / str(f) for f in LIST_ITEM_FILE_NAMES]
MAPPED_ITEM_FILE_NAMES = os.listdir(DIR_MAP)
sorted(MAPPED_ITEM_FILE_NAMES)
MAPPED_FILE_PATHS = [DIR_MAP / str(f) for f in MAPPED_ITEM_FILE_NAMES]


class TestNSB2023Parsers(TestCase):
    """Tests methods in NSB2023Mapping class"""

    @classmethod
    def setUpClass(cls):
        """Load json files before running tests."""
        cls.list_items = cls._load_json_files()

    @staticmethod
    def _load_json_files() -> List[Tuple[dict, dict, str]]:
        """Reads raw data and expected data into json"""
        list_items = []
        for file_path in LIST_ITEM_FILE_PATHS:
            mapped_file_path = (
                file_path.parent.parent
                / "mapped"
                / ("mapped_" + file_path.name)
            )
            with open(file_path) as f:
                contents = json.load(f)
            with open(mapped_file_path) as f:
                mapped_contents = json.load(f)
            list_items.append((contents, mapped_contents, file_path.name))
            list_items.sort(key=lambda x: x[2])
        return list_items

    def test_parser(self):
        """Checks that raw data is parsed correctly"""
        for list_item in self.list_items:
            raw_data = list_item[0]
            expected_mapped_data = list(list_item[1])
            expected_mapped_data.sort(key=lambda x: str(x))
            raw_file_name = list_item[2]
            logging.debug(f"Processing file: {raw_file_name}")
            nsb_model = NSBList2023.parse_obj(raw_data)
            mapper = NSB2023Mapping()
            mapped_procedure = mapper.map_nsb_model(nsb_model)
            mapped_procedure_json = [
                json.loads(p.json()) for p in mapped_procedure
            ]
            mapped_procedure_json.sort(key=lambda x: str(x))
            self.assertEqual(expected_mapped_data, mapped_procedure_json)

    def test_craniotomy_edge_case(self):
        """Tests other craniotomy cases"""

        # Check WHC type
        list_item = self.list_items[2]
        raw_data = deepcopy(list_item[0])
        raw_data["Procedure"] = "WHC NP"
        raw_data["CraniotomyType"] = "WHC"
        nsb_model1 = NSBList2023.parse_obj(raw_data)
        mapper = NSB2023Mapping()
        mapped_procedure1 = mapper.map_nsb_model(nsb_model1)
        mapped_procedure1.sort(key=lambda x: str(x))
        cran_proc1 = mapped_procedure1[0]
        self.assertEqual(
            CraniotomyType.WHC, getattr(cran_proc1, "craniotomy_type")
        )

        # Check OTHER type
        raw_data["Procedure"] = "WHC NP"
        raw_data["CraniotomyType"] = "Other"
        nsb_model2 = NSBList2023.parse_obj(raw_data)
        mapped_procedure2 = mapper.map_nsb_model(nsb_model2)
        mapped_procedure2.sort(key=lambda x: str(x))
        cran_proc2 = mapped_procedure2[0]
        self.assertEqual(
            CraniotomyType.OTHER, getattr(cran_proc2, "craniotomy_type")
        )

    def test_injection_edge_case(self):
        """Tests the case where there is an INJ procedure, but the inj types
        are malformed. It should create generic BrainInjection objects."""
        list_item = self.list_items[3]
        raw_data = deepcopy(list_item[0])
        raw_data["Inj1Type"] = "Select..."
        raw_data["ImplantIDCoverslipType"] = "3.5"
        nsb_model = NSBList2023.parse_obj(raw_data)
        mapper = NSB2023Mapping()
        mapped_procedure = mapper.map_nsb_model(nsb_model)
        mapped_virus_strain = mapper._map_virus_strain_to_materials("abc-def")
        mapped_virus_strain_none = mapper._map_virus_strain_to_materials(None)
        mapped_coordinate_ref = mapper._map_ap_info_to_coord_reference(None)
        self.assertEqual(
            InjectionMaterial.construct(full_genome_name="abc-def"),
            mapped_virus_strain,
        )
        self.assertIsNone(mapped_virus_strain_none)
        self.assertIsNone(mapped_coordinate_ref)
        self.assertIsNotNone(mapped_procedure)

    def test_burr_hole_to_probe_edge_case(self):
        """Tests edge case where burr hole number is 5"""
        mapper = NSB2023Mapping()
        self.assertIsNone(mapper._map_burr_hole_number_to_probe(5))


if __name__ == "__main__":
    unittest_main()
