"""Tests for the imaging utils module."""

import unittest
from datetime import datetime
from fastapi.responses import JSONResponse
from aind_metadata_service.slims.imaging.utils import (
    validate_parameters,
    parse_date_performed,
    filter_by_date,
    get_latest_metadata,
    format_response,
)


class TestUtils(unittest.TestCase):

    def test_validate_parameters(self):
        """Test validate_parameters to prevent conflicting parameters."""
        response = validate_parameters("2024-01-01", True)
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, 400)

        response = validate_parameters(None, False)
        self.assertIsNone(response)

        response = validate_parameters("2024-01-01", False)
        self.assertIsNone(response)

    def test_parse_date_performed(self):
        """Test parse_date_performed for valid and invalid date inputs."""
        self.assertEqual(
            parse_date_performed("2024-10-18T22:27:00"),
            datetime(2024, 10, 18, 22, 27, 0),
        )
        self.assertEqual(
            parse_date_performed("2024-10-18T22:27"),
            datetime(2024, 10, 18, 22, 27, 0),
        )
        self.assertIsNone(parse_date_performed(None))
        self.assertIsNone(parse_date_performed(""))
        self.assertIsInstance(
            parse_date_performed("invalid-date"), JSONResponse
        )

    def test_filter_by_date(self):
        """Test filter_by_date to ensure it correctly filters metadata."""
        imaging_metadata = [
            {"date_performed": "2024-10-18T22:27:00"},
            {"date_performed": "2024-10-19T15:45:00"},
        ]
        date_performed = datetime(2024, 10, 18, 22, 27, 0)
        result = filter_by_date(imaging_metadata, date_performed)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["date_performed"], "2024-10-18T22:27:00")

    def test_get_latest_metadata(self):
        """Test get_latest_metadata to ensure it returns the most recent item."""
        imaging_metadata = [
            {"date_performed": "2024-10-18T22:27:00"},
            {"date_performed": "2024-10-19T15:45:00"},
            {"date_performed": "2024-10-20T10:15:00"},
        ]
        result = get_latest_metadata(imaging_metadata)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["date_performed"], "2024-10-20T10:15:00")

    def test_format_response(self):
        """Test format_response for different metadata scenarios."""
        response = format_response(
            [
                {"date_performed": "2024-10-18T22:27:00"},
                {"date_performed": "2024-10-19T15:45:00"},
            ]
        )
        self.assertEqual(response.status_code, 300)

        response = format_response([{"date_performed": "2024-10-18T22:27:00"}])
        self.assertEqual(response.status_code, 200)

        response = format_response([])
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
