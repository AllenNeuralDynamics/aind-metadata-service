import json
import logging
import os
from pathlib import Path
from typing import List
from unittest import TestCase, main as unittest_main
from unittest.mock import patch
from aind_metadata_service.sharepoint.nsb2019.models import NSBList2019
from aind_metadata_service.sharepoint.nsb2019.client import ListClient

if os.getenv("LOG_LEVEL"):  # pragma: no cover
    logging.basicConfig(level=os.getenv("LOG_LEVEL"))

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".."
SHAREPOINT_DIR = TEST_DIR / "resources" / "sharepoint" / "nsb2019"
LIST_ITEM_FILE_NAMES = os.listdir(SHAREPOINT_DIR)
LIST_ITEM_FILE_PATHS = [SHAREPOINT_DIR / str(f) for f in LIST_ITEM_FILE_NAMES]


class TestNSB2019Parsers(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.list_items = cls._load_json_files()

    @staticmethod
    def _load_json_files() -> List[dict]:
        list_items = []
        for file_path in LIST_ITEM_FILE_PATHS:
            with open(file_path) as f:
                contents = json.load(f)
            list_items.append(contents)
        return list_items

    @patch("office365.sharepoint.client_context.ClientContext")
    def test_parser(self, mocked_ctx):
        list_item = self.list_items[0]
        nsb_model = NSBList2019.parse_obj(list_item)
        list_client = ListClient(
            client_context=mocked_ctx,
            subject_id="12345", list_title="List 2019")
        procedures = list_client._map_nsb_model(nsb_model)
        print(procedures)

        return None


if __name__ == "__main__":
    unittest_main()

