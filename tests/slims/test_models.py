"""Test models module in slims package"""

import json
import os
import unittest
from pathlib import Path

from slims.internal import Record

from aind_metadata_service.slims.models import (
    ContentsTableColumnInfo,
    ContentsTableRow,
)

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".."
EXAMPLE_PATH = TEST_DIR / "resources" / "slims" / "json_entity.json"


class TestContentsTableRow(unittest.TestCase):
    """Class to test methods for ContentsTableRow."""

    @classmethod
    def setUpClass(cls):
        """Load record object before running tests."""
        with open(EXAMPLE_PATH, "r") as f:
            json_entity = json.load(f)
        # Turning off type check on slims_api argument
        # noinspection PyTypeChecker
        record_object = Record(json_entity=json_entity, slims_api=None)
        cls.example_record = record_object

    def test_slims_model(self):
        """Tests model response"""
        model = ContentsTableRow.from_record(self.example_record)
        self.assertEqual(0, model.ingredientCount)

    def test_map_record_to_model_string(self):
        """Tests model generator"""
        field_str_list = ContentsTableRow.map_record_to_model_string(
            self.example_record
        )

        self.assertEqual(
            (
                "cntn_fk_originalContent: Optional[str] = "
                'Field(None, title="Original Content")'
            ),
            field_str_list[0],
        )


class TestContentsTableColumnInfo(unittest.TestCase):
    """Class to test methods for ContentsTableColumnInfo."""

    def test_edge_cases(self):
        """Tests a few edge cases in field str generation"""
        row1 = ContentsTableColumnInfo(
            datatype="DATE",
            editable=True,
            hidden=False,
            name="some_date",
            title="Some Date",
            position=0,
        )
        row2 = ContentsTableColumnInfo(
            datatype="QUANTITY",
            editable=True,
            hidden=False,
            name="some_quantity",
            title="Some Quantity",
            position=0,
        )
        field_str1 = row1.map_to_field_str()
        field_str2 = row2.map_to_field_str()
        self.assertEqual(
            'some_date: Optional[datetime] = Field(None, title="Some Date")',
            field_str1,
        )
        self.assertEqual(
            (
                "some_quantity: Optional[float] = "
                'Field(None, title="Some Quantity")'
            ),
            field_str2,
        )


if __name__ == "__main__":
    unittest.main()
