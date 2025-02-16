"""Tests methods in table_handler module."""

import unittest
from datetime import datetime, timezone

from aind_metadata_service.slims.table_handler import SlimsTableHandler


# TODO: Add more tests
class TestSlimsTableHandler(unittest.TestCase):
    """Test class for SlimsTableHandler"""

    def test_get_date_criteria_start_no_end(self):
        """Tests get_date_criteria when start date and no end date"""
        criteria = SlimsTableHandler._get_date_criteria(
            start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            end_date=None,
            field_name="xprn_createdOn",
        )
        expected_criteria = {
            "fieldName": "xprn_createdOn",
            "operator": "greaterOrEqual",
            "value": 1735689600000,
        }
        self.assertEqual(expected_criteria, criteria.to_dict())

    def test_get_date_criteria_no_start_with_end(self):
        """Tests get_date_criteria when end date and no start date"""
        criteria = SlimsTableHandler._get_date_criteria(
            end_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            start_date=None,
            field_name="xprn_createdOn",
        )
        expected_criteria = {
            "fieldName": "xprn_createdOn",
            "operator": "lessOrEqual",
            "value": 1735689600000,
        }
        self.assertEqual(expected_criteria, criteria.to_dict())

    def test_get_date_criteria_start_with_end(self):
        """Tests get_date_criteria when end date and start date"""
        criteria = SlimsTableHandler._get_date_criteria(
            end_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            start_date=datetime(2025, 2, 1, tzinfo=timezone.utc),
            field_name="xprn_createdOn",
        )
        expected_criteria = {
            "operator": "and",
            "criteria": [
                {
                    "fieldName": "xprn_createdOn",
                    "operator": "greaterOrEqual",
                    "value": 1738368000000,
                },
                {
                    "fieldName": "xprn_createdOn",
                    "operator": "lessOrEqual",
                    "value": 1735689600000,
                },
            ],
        }

        self.assertEqual(expected_criteria, criteria.to_dict())


if __name__ == "__main__":
    unittest.main()
