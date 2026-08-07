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
                "FormattedValue": "Jaimie Kenney",
                "statuscode@OData.Community.Display.V1."
                "FormattedValue": "Active",
                "statuscode": 1,
                "aibs_weight": 22.1,
                "aibs_fact_mouse_weight_recordsid": (
                    "53882aa8-8592-f111-8077-3833c5ef5e4a"
                ),
                "aibs_date_time": "2026-08-07T17:30:14.710665+00:00",
                "aibs_software_source": "WL",
                "aibs_is_baseline_weight": False,
                "aibs_workstation": "FRG.13-D",
                "aibs_software_version": "4.1.0.dev7",
                "_aibs_mouse_id_value@OData.Community.Display.V1."
                "FormattedValue": "864846",
                "aibs_notes": "Test note"
            }
        ]

        result = map_mouse_weight_records(raw_response)

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], MouseWeightData)
        self.assertEqual(
            result[0].record_id, "53882aa8-8592-f111-8077-3833c5ef5e4a"
        )
        self.assertEqual(result[0].mouse_id, "864846")
        self.assertEqual(result[0].weight, 22.1)
        self.assertEqual(result[0].operator, "Jaimie Kenney")
        self.assertEqual(result[0].workstation, "FRG.13-D")
        self.assertEqual(result[0].software_version, "4.1.0.dev7")
        self.assertEqual(result[0].software_source, "WL")
        self.assertEqual(result[0].status, "Active")
        self.assertFalse(result[0].is_baseline_weight)
        self.assertEqual(result[0].notes, "Test note")
        self.assertIsInstance(result[0].weight_datetime, datetime)

    def test_map_mouse_weight_records_empty(self):
        """Test mapping with empty response"""
        result = map_mouse_weight_records([])
        self.assertEqual(result, [])

    def test_map_mouse_weight_records_none(self):
        """Test mapping with None response"""
        result = map_mouse_weight_records(None)
        self.assertEqual(result, [])

    def test_map_mouse_weight_records_multiple(self):
        """Test mapping multiple records"""
        raw_response = [
            {
                "aibs_fact_mouse_weight_recordsid": "record-1",
                "_aibs_mouse_id_value@OData.Community.Display.V1."
                "FormattedValue": "123456",
                "aibs_weight": 25.5,
                "cr138_datetime": "2026-08-07T10:00:00Z",
            },
            {
                "aibs_fact_mouse_weight_recordsid": "record-2",
                "_aibs_mouse_id_value@OData.Community.Display.V1."
                "FormattedValue": "789012",
                "aibs_weight": 23.2,
                "cr138_datetime": "2026-08-07T11:00:00Z",
            }
        ]

        result = map_mouse_weight_records(raw_response)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].record_id, "record-1")
        self.assertEqual(result[0].mouse_id, "123456")
        self.assertEqual(result[0].weight, 25.5)
        self.assertEqual(result[1].record_id, "record-2")
        self.assertEqual(result[1].mouse_id, "789012")
        self.assertEqual(result[1].weight, 23.2)

    def test_map_mouse_weight_records_missing_fields(self):
        """Test mapping with missing optional fields"""
        raw_response = [
            {
                "aibs_fact_mouse_weight_recordsid": "record-1",
                "aibs_weight": 25.5,
                # Missing most optional fields
            }
        ]

        result = map_mouse_weight_records(raw_response)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].record_id, "record-1")
        self.assertEqual(result[0].weight, 25.5)
        self.assertIsNone(result[0].mouse_id)
        self.assertIsNone(result[0].operator)
        self.assertIsNone(result[0].weight_datetime)

    def test_map_mouse_weight_records_prefers_aibs_date_time(self):
        """Test that aibs_date_time is preferred over cr138_datetime"""
        raw_response = [
            {
                "aibs_fact_mouse_weight_recordsid": "record-1",
                "aibs_date_time": "2026-08-07T17:30:14.710665+00:00",
                "cr138_datetime": "2026-08-07T17:30:14Z",
            }
        ]

        result = map_mouse_weight_records(raw_response)

        # aibs_date_time has microseconds, cr138_datetime doesn't
        self.assertEqual(result[0].weight_datetime.microsecond, 710665)

    def test_map_mouse_weight_records_fallback_to_cr138_datetime(self):
        """Test fallback to cr138_datetime when aibs_date_time is missing"""
        raw_response = [
            {
                "aibs_fact_mouse_weight_recordsid": "record-1",
                "cr138_datetime": "2026-08-07T17:30:14Z",
                # aibs_date_time is missing
            }
        ]

        result = map_mouse_weight_records(raw_response)

        self.assertIsNotNone(result[0].weight_datetime)
        self.assertEqual(result[0].weight_datetime.microsecond, 0)

    def test_parse_datetime(self):
        """Test parsing datetime strings from Dataverse"""
        result = _parse_datetime("2026-08-07T17:30:14Z")
        self.assertIsNotNone(result)
        self.assertEqual(result.year, 2026)
        self.assertEqual(result.month, 8)
        self.assertEqual(result.day, 7)
        self.assertIsNone(_parse_datetime(None))
        self.assertIsNone(_parse_datetime("invalid"))
