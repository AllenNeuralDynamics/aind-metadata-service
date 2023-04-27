"""Tests sharepoint.mol_anatomy.mapping module"""

import json
import os
from pathlib import Path
from unittest import TestCase
from unittest import main as unittest_main

import pandas as pd

from aind_metadata_service.sharepoint.mol_anatomy.models import ExcelSheetRow

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".."
EXAMPLE_FILE = (
    TEST_DIR / "resources" / "sharepoint" / "mol_anatomy" / "MouseTracker.xlsx"
)


class TestMolAnatomyModels(TestCase):
    """Tests methods in MolAnatomyModels Class"""

    def test_excel_sheet_parsing(self):
        """Tests excel sheets are parsed into models without error"""
        excel_sheets = pd.read_excel(EXAMPLE_FILE, sheet_name=None)
        list_of_records = []
        for sheet_name in [
            sn
            for sn in excel_sheets
            if not ExcelSheetRow.ignore_excel_sheet(
                excel_sheet_name=sn, column_names=excel_sheets[sn].columns
            )
        ]:
            df = excel_sheets[sheet_name]
            json_list = json.loads(df.to_json(orient="records"))
            for j in json_list:
                row = ExcelSheetRow.parse_obj(j)
                list_of_records.append(row)
        self.assertIsNotNone(list_of_records)

    def test_volume_parser(self):
        """Tests edge case for volume_injected field"""
        excel_sheets = pd.read_excel(EXAMPLE_FILE, sheet_name=None)
        df = excel_sheets["ePet-Cre_PK"]
        json_list = json.loads(df.to_json(orient="records"))
        sample_json_row = json_list[1]
        sample_json_row["Volume Injected"] = "5"
        sample_model = ExcelSheetRow.parse_obj(sample_json_row)
        self.assertEqual(5, sample_model.volume_injected.number)


if __name__ == "__main__":
    unittest_main()
