"""Tests methods in table_handler module."""

import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from aind_metadata_service.slims.table_handler import (
    SlimsTableHandler,
    parse_html,
)


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

    def test_parse_html(self):
        """Tests parse html"""
        protocol_html = '<a href="https://example.com">Example</a>'
        output = parse_html(protocol_html)
        self.assertEqual("https://example.com", output)

    def test_parse_malformed_html(self):
        """Tests parse_html when malformed string"""
        protocol_html = "<a>Missing Href</a>"
        output = parse_html(protocol_html)
        self.assertIsNone(output)

    def test_parse_non_html(self):
        """Tests parse_html when regular string passed in"""
        protocol_html = "Not in HTML"
        output = parse_html(protocol_html)
        self.assertEqual("Not in HTML", output)

    @patch("logging.warning")
    def test_parse_error(self, mock_log_warn: MagicMock):
        """Tests parse_html when regular string passed in"""

        output = parse_html(123)  # type: ignore
        self.assertIsNone(output)
        mock_log_warn.assert_called_once()


if __name__ == "__main__":
    unittest.main()
