"""Tests sharepoint.mol_anatomy.mapping module"""

import os
from datetime import datetime
from pathlib import Path
from unittest import TestCase
from unittest import main as unittest_main
from unittest.mock import MagicMock, patch

import pandas as pd
import pytz
from aind_data_schema.procedures import RetroOrbitalInjection

from aind_metadata_service.sharepoint.mol_anatomy.mapping import (
    MolecularAnatomyMapping,
)
from aind_metadata_service.sharepoint.mol_anatomy.models import ExcelSheetRow

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".."
EXAMPLE_FILE = (
    TEST_DIR / "resources" / "sharepoint" / "mol_anatomy" / "MouseTracker.xlsx"
)


class TestMolAnatomyMapping(TestCase):
    """Tests methods in MolAnatomyMapping Class"""

    def test_excel_sheet_parsing(self):
        """Tests that the excel information is parsed without error."""
        excel_sheets = pd.read_excel(EXAMPLE_FILE, sheet_name=None)
        filtered_records = MolecularAnatomyMapping._apply_filter(
            excel_sheets=excel_sheets, subject_id="650008"
        )
        procedures = []
        for record in filtered_records:
            procedures.extend(
                MolecularAnatomyMapping.map_model(sharepoint_model=record)
            )
        expected_procedures = [
            RetroOrbitalInjection.construct(
                start_date=datetime(2022, 10, 4, tzinfo=pytz.UTC),
                end_date=datetime(2022, 10, 4, tzinfo=pytz.UTC),
            )
        ]
        self.assertEqual(expected_procedures, procedures)

    def test_empty_mapping(self):
        """Tests that an empty list is returned if no procedure found."""
        mapper = MolecularAnatomyMapping()
        procedures = mapper.map_model(
            sharepoint_model=ExcelSheetRow.construct()
        )
        self.assertEqual([], procedures)

    @patch(
        "aind_metadata_service.sharepoint.mol_anatomy.mapping.ClientContext"
    )
    def test_get_procedure_info(self, mocked_client: MagicMock):
        """Tests the get_procedure_info method"""
        mocked_get_file = MagicMock()
        mocked_client.web.get_file_by_guest_url.return_value = mocked_get_file
        mocked_file_query = MagicMock()
        mocked_get_file.expand.return_value.get.return_value.execute_query = (
            mocked_file_query
        )
        mocked_binary_stream = MagicMock()
        mocked_file_query.return_value.open_binary_stream.return_value = (
            mocked_binary_stream
        )
        mocked_file_stream = MagicMock()
        mocked_binary_stream.execute_query.return_value = mocked_file_stream
        mocked_file_stream.value = EXAMPLE_FILE

        mapper = MolecularAnatomyMapping()
        procedures = mapper.get_procedures_from_sharepoint(
            subject_id="650008",
            client_context=mocked_client,
            list_title="some_url",
        )
        expected_procedures = [
            RetroOrbitalInjection.construct(
                start_date=datetime(2022, 10, 4, tzinfo=pytz.UTC),
                end_date=datetime(2022, 10, 4, tzinfo=pytz.UTC),
            )
        ]
        self.assertEqual(expected_procedures, procedures)


if __name__ == "__main__":
    unittest_main()
