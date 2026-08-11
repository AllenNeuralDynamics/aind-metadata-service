"""Module to test dataverse mapper"""

import unittest
from datetime import datetime

from aind_metadata_service_server.mappers.dataverse import (
    _parse_datetime,
    filter_dataverse_metadata,
    map_mouse_weight_records,
)
from aind_metadata_service_server.models import MouseWeightData


class TestDataverseMapper(unittest.TestCase):
    """Class to test methods for Dataverse mapper."""

    def test_filter_removes_metadata_keys(self):
        """Test that only formatted value and non-metadata fields are kept."""
        formatted_value = "@OData.Community.Display.V1.FormattedValue"

        data = {
            "@data.etag": "some-etag",
            "_private": "some-private-data",
            "statecode@OData": "some-state",
            "data": "some-data",
            "_ownerid_value": "some-lookup-id",
            f"_ownerid_value{formatted_value}": "owner-formatted",
            "nested": {
                "@meta": "some-meta",
                "keep": 123,
                "_hidden": "some-hidden",
                "_something_value": "lookup-nested",
                f"_something_value{formatted_value}": "something-formatted",
            },
            "list": [
                {
                    "bar@Odata": 2,
                    "bar": 2,
                    "_lookup_value": "some-lookup-id",
                    f"_lookup_value{formatted_value}": "lookup-formatted",
                },
                {
                    "foo@Odata": 4,
                    "_foo": 4,
                    "_ownerid_value": "some-lookup-id",
                    f"_ownerid_value{formatted_value}": "owner-list-formatted",
                },
            ],
        }
        filtered = filter_dataverse_metadata(data)

        expected = {
            "data": "some-data",
            f"_ownerid_value{formatted_value}": "owner-formatted",
            "nested": {
                "keep": 123,
                f"_something_value{formatted_value}": "something-formatted",
            },
            "list": [
                {
                    "bar": 2,
                    f"_lookup_value{formatted_value}": "lookup-formatted",
                },
                {f"_ownerid_value{formatted_value}": "owner-list-formatted"},
            ],
        }
        self.assertEqual(filtered, expected)

    def test_map_mouse_weight_records_success(self):
        """Test successful mapping of mouse weight records"""
        raw_response = [
            {
                "cr138_datetime": "2026-08-07T17:30:14Z",
                "_aibs_operator_value@OData.Community.Display.V1."
                "FormattedValue": "John Doe",
                "statuscode@OData.Community.Display.V1."
                "FormattedValue": "Active",
                "statuscode": 1,
                "aibs_weight": 22.1,
                "aibs_fact_mouse_weight_recordsid": (
                    "test-record-12345678-1234-1234-1234-123456789abc"
                ),
                "aibs_software_source": "WL",
                "aibs_is_baseline_weight": False,
                "aibs_workstation": "TEST-WORKSTATION-1",
                "aibs_software_version": "4.1.0.dev7",
                "_aibs_mouse_id_value@OData.Community.Display.V1."
                "FormattedValue": "123456",
                "aibs_notes": "Test note",
            }
        ]

        result = map_mouse_weight_records(raw_response)

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], MouseWeightData)
        self.assertEqual(
            result[0].record_id,
            "test-record-12345678-1234-1234-1234-123456789abc",
        )
        self.assertEqual(result[0].mouse_id, "123456")
        self.assertEqual(result[0].weight, 22.1)
        self.assertEqual(result[0].operator, "John Doe")
        self.assertEqual(result[0].workstation, "TEST-WORKSTATION-1")
        self.assertEqual(result[0].software_version, "4.1.0.dev7")
        self.assertEqual(result[0].software_source, "WL")
        self.assertEqual(result[0].status, "Active")
        self.assertFalse(result[0].is_baseline_weight)
        self.assertEqual(result[0].notes, "Test note")
        self.assertIsInstance(result[0].weight_datetime, datetime)

    def test_map_mouse_weight_records_empty_or_none(self):
        """Test mapping with empty or None response"""
        self.assertEqual(map_mouse_weight_records([]), [])
        self.assertEqual(map_mouse_weight_records(None), [])

    def test_map_mouse_weight_records_multiple(self):
        """Test mapping multiple records"""
        raw_response = [
            {
                "aibs_fact_mouse_weight_recordsid": "test-record-1",
                "_aibs_mouse_id_value@OData.Community.Display.V1."
                "FormattedValue": "111111",
                "aibs_weight": 25.5,
                "cr138_datetime": "2026-08-07T10:00:00Z",
            },
            {
                "aibs_fact_mouse_weight_recordsid": "test-record-2",
                "_aibs_mouse_id_value@OData.Community.Display.V1."
                "FormattedValue": "222222",
                "aibs_weight": 23.2,
                "cr138_datetime": "2026-08-07T11:00:00Z",
            },
        ]

        result = map_mouse_weight_records(raw_response)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].record_id, "test-record-1")
        self.assertEqual(result[0].mouse_id, "111111")
        self.assertEqual(result[0].weight, 25.5)
        self.assertEqual(result[1].record_id, "test-record-2")
        self.assertEqual(result[1].mouse_id, "222222")
        self.assertEqual(result[1].weight, 23.2)

    def test_map_mouse_weight_records_missing_fields(self):
        """Test mapping with missing optional fields"""
        raw_response = [
            {
                "aibs_fact_mouse_weight_recordsid": "test-record-minimal",
                "aibs_weight": 25.5,
            }
        ]

        result = map_mouse_weight_records(raw_response)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].record_id, "test-record-minimal")
        self.assertEqual(result[0].weight, 25.5)
        self.assertIsNone(result[0].mouse_id)

    def test_map_mouse_weight_records_datetime_handling(self):
        """Test datetime field parsing from cr138_datetime"""
        raw_response = [
            {
                "aibs_fact_mouse_weight_recordsid": "test-record-datetime",
                "cr138_datetime": "2026-08-07T17:30:14Z",
            }
        ]
        result = map_mouse_weight_records(raw_response)
        self.assertIsNotNone(result[0].weight_datetime)
        self.assertEqual(result[0].weight_datetime.year, 2026)
        self.assertEqual(result[0].weight_datetime.month, 8)
        self.assertEqual(result[0].weight_datetime.day, 7)
        self.assertEqual(result[0].weight_datetime.hour, 17)
        self.assertEqual(result[0].weight_datetime.minute, 30)
        self.assertEqual(result[0].weight_datetime.second, 14)

    def test_parse_datetime(self):
        """Test parsing datetime strings from Dataverse"""
        result = _parse_datetime("2026-08-07T17:30:14Z")
        self.assertIsNotNone(result)
        self.assertEqual(result.year, 2026)
        self.assertEqual(result.month, 8)
        self.assertEqual(result.day, 7)
        self.assertIsNone(_parse_datetime(None))
        self.assertIsNone(_parse_datetime("invalid"))
