"""Tests for the imaging utils module."""

import unittest
from datetime import datetime, timezone
from aind_metadata_service.slims.imaging.utils import (
    parse_date_performed,
    filter_by_date,
    get_latest_metadata,
)
from aind_metadata_service.models import SpimImagingInformation


class TestUtils(unittest.TestCase):
    """Tests methods in Imaging Utils."""

    def test_parse_date_performed(self):
        """Test parse_date_performed for valid and invalid date inputs."""
        self.assertEqual(
            parse_date_performed("2024-10-18T22:27:01"),
            datetime(2024, 10, 18, 22, 27, 0),
        )
        self.assertEqual(
            parse_date_performed("2024-10-18T22:27"),
            datetime(2024, 10, 18, 22, 27, 0),
        )
        self.assertIsNone(parse_date_performed(None))
        self.assertIsNone(parse_date_performed(""))
        self.assertIsNone(parse_date_performed("invalid-date"))

    def test_filter_by_date(self):
        """Test filter_by_date to ensure it correctly filters metadata."""
        date_performed = datetime(2024, 10, 18, 22, 27, 0, tzinfo=timezone.utc)
        imaging_metadata = [
            SpimImagingInformation.model_construct(
                date_performed=date_performed
            ),
            SpimImagingInformation.model_construct(
                date_performed=datetime(
                    2024, 10, 19, 15, 45, 0, tzinfo=timezone.utc
                )
            ),
        ]
        result = filter_by_date(imaging_metadata, date_performed)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].date_performed, date_performed)

    def test_get_latest_metadata(self):
        """Test get_latest_metadata returns most recent imaging."""
        imaging_metadata = [
            SpimImagingInformation.model_construct(
                date_performed=datetime(
                    2024, 10, 18, 22, 27, 0, tzinfo=timezone.utc
                )
            ),
            SpimImagingInformation.model_construct(
                date_performed=datetime(
                    2024, 10, 19, 15, 45, 0, tzinfo=timezone.utc
                )
            ),
        ]
        result = get_latest_metadata(imaging_metadata)
        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0].date_performed,
            datetime(2024, 10, 19, 15, 45, 0, tzinfo=timezone.utc),
        )


if __name__ == "__main__":
    unittest.main()
