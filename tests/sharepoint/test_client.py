"""Module to test SharePoint Client methods"""

import json
import logging
import os
import unittest
from pathlib import Path
from typing import List, Tuple
from unittest.mock import MagicMock, patch

from aind_metadata_service.sharepoint.client import SharePointClient

if os.getenv("LOG_LEVEL"):  # pragma: no cover
    logging.basicConfig(level=os.getenv("LOG_LEVEL"))

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".."
DIR_RAW_2019 = TEST_DIR / "resources" / "sharepoint" / "nsb2019" / "raw"
DIR_MAP_2019 = TEST_DIR / "resources" / "sharepoint" / "nsb2019" / "mapped"
LIST_ITEM_FILE_NAMES_2019 = os.listdir(DIR_RAW_2019)
sorted(LIST_ITEM_FILE_NAMES_2019)
LIST_ITEM_FILE_PATHS_2019 = [
    DIR_RAW_2019 / str(f) for f in LIST_ITEM_FILE_NAMES_2019
]
MAPPED_ITEM_FILE_NAMES_2019 = os.listdir(DIR_MAP_2019)
sorted(MAPPED_ITEM_FILE_NAMES_2019)
MAPPED_FILE_PATHS_2019 = [
    DIR_MAP_2019 / str(f) for f in MAPPED_ITEM_FILE_NAMES_2019
]
DIR_RAW_2023 = TEST_DIR / "resources" / "sharepoint" / "nsb2023" / "raw"
DIR_MAP_2023 = TEST_DIR / "resources" / "sharepoint" / "nsb2023" / "mapped"
LIST_ITEM_FILE_NAMES_2023 = os.listdir(DIR_RAW_2023)
sorted(LIST_ITEM_FILE_NAMES_2023)
LIST_ITEM_FILE_PATHS_2023 = [
    DIR_RAW_2023 / str(f) for f in LIST_ITEM_FILE_NAMES_2023
]
MAPPED_ITEM_FILE_NAMES_2023 = os.listdir(DIR_MAP_2023)
sorted(MAPPED_ITEM_FILE_NAMES_2023)
MAPPED_FILE_PATHS_2023 = [
    DIR_MAP_2023 / str(f) for f in MAPPED_ITEM_FILE_NAMES_2023
]


class TestSharepointClient(unittest.TestCase):
    """Class to test methods for SharePointClient."""

    @classmethod
    def setUpClass(cls):
        """Load json files before running tests."""
        cls.list_items_2019 = cls._load_json_files(year="2019")
        cls.list_items_2023 = cls._load_json_files(year="2023")

    @staticmethod
    def _load_json_files(year: str) -> List[Tuple[dict, dict, str]]:
        """Reads raw data and expected data into json"""
        list_items = []
        if year == "2019":
            list_item_file_paths = LIST_ITEM_FILE_PATHS_2019
        else:
            list_item_file_paths = LIST_ITEM_FILE_PATHS_2023
        for file_path in list_item_file_paths:
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

    @patch("aind_metadata_service.sharepoint.client.ClientContext")
    def test_empty_response(self, mock_sharepoint_client: MagicMock):
        """Tests that an empty response is generated if no data returned
        from NSB datatbases"""
        client = SharePointClient(
            nsb_site_url="some_url",
            nsb_list_title_2019="some_list_title2019",
            nsb_list_title_2023="some_list_title2023",
            client_id="some_client_id",
            client_secret="some_client_secret",
        )
        response = client.get_procedure_info(subject_id="12345")
        mock_sharepoint_client.assert_called()
        self.assertEqual(404, response.status_code)

    @patch("aind_metadata_service.sharepoint.client.ClientContext")
    def test_data_mapped(self, mock_sharepoint_client: MagicMock):
        """Tests that 200 response returned correctly."""

        inner_mock = MagicMock()
        mock_sharepoint_client.return_value.with_credentials.return_value = (
            inner_mock
        )
        mock_list_views = MagicMock()
        inner_mock.web.lists.get_by_title.return_value.views = mock_list_views
        mock_list_items = MagicMock()
        mock_list_views.get_by_title.return_value.get_items.return_value = (
            mock_list_items
        )
        list_item_2019_1 = self.list_items_2019[0][0]
        list_item_2023_1 = self.list_items_2023[0][0]
        mock_list_item2019 = MagicMock()
        mock_list_item2023 = MagicMock()
        mock_list_item2019.to_json.return_value = list_item_2019_1
        mock_list_item2023.to_json.return_value = list_item_2023_1
        mock_list_items.filter.side_effect = [
            [mock_list_item2019],
            [mock_list_item2023],
        ]

        client = SharePointClient(
            nsb_site_url="some_url",
            nsb_list_title_2019="some_list_title2019",
            nsb_list_title_2023="some_list_title2023",
            client_id="some_client_id",
            client_secret="some_client_secret",
        )

        expected_subject_procedures = []
        expected_subject_procedures.extend(self.list_items_2019[0][1])
        expected_subject_procedures.extend(self.list_items_2023[0][1])
        response = client.get_procedure_info(subject_id="12345")
        contents = json.loads(response.body.decode("utf-8"))
        expected_subject_procedures.sort(key=lambda x: str(x))
        contents["data"]["subject_procedures"].sort(key=lambda x: str(x))
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            expected_subject_procedures, contents["data"]["subject_procedures"]
        )


if __name__ == "__main__":
    unittest.main()
