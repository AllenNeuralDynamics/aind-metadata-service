from aind_metadata_service.sharepoint.mol_anatomy.models import ExcelSheetRow
from aind_metadata_service.sharepoint.mol_anatomy.mapping import (
    MolecularAnatomyMapping,
)
import os
import json
from pathlib import Path
import pandas as pd
from unittest import TestCase
from unittest import main as unittest_main

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".."
EXAMPLE_FILE = (
    TEST_DIR / "resources" / "sharepoint" / "mol_anatomy" / "MouseTracker.xlsx"
)


class TestMolAnatomyModels(TestCase):
    def test_excel_sheet_parsing(self):
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
                list_of_records.extend(row)


if __name__ == "__main__":
    unittest_main()
