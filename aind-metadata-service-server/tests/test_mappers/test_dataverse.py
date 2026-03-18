"""Module to test dataverse mapper"""

import unittest
from fastapi import HTTPException

from aind_metadata_service_server.mappers.dataverse import (
    filter_dataverse_metadata,
    apply_query_parameters,
)


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

    def test_apply_query_parameters_no_filters(self):
        """Test that no filters returns original data."""
        data = {"value": [{"id": "1", "name": "Test"}]}
        result = apply_query_parameters(data, {})
        self.assertEqual(result, data)

    def test_apply_query_parameters_single_filter(self):
        """Test filtering with single parameter."""
        data = {
            "value": [
                {"id": "1", "status": "active"},
                {"id": "2", "status": "inactive"},
            ]
        }
        result = apply_query_parameters(data, {"status": "active"})
        expected = {"value": [{"id": "1", "status": "active"}]}
        self.assertEqual(result, expected)

    def test_apply_query_parameters_multiple_filters(self):
        """Test filtering with multiple parameters (AND logic)."""
        data = {
            "value": [
                {"id": "1", "status": "active", "owner": "alice"},
                {"id": "2", "status": "active", "owner": "bob"},
            ]
        }
        result = apply_query_parameters(
            data, {"status": "active", "owner": "alice"}
        )
        expected = {
            "value": [{"id": "1", "status": "active", "owner": "alice"}]
        }
        self.assertEqual(result, expected)

    def test_apply_query_parameters_case_insensitive(self):
        """Test that filtering is case-insensitive."""
        data = {"value": [{"id": "1", "status": "Active"}]}
        result = apply_query_parameters(data, {"status": "active"})
        expected = {"value": [{"id": "1", "status": "Active"}]}
        self.assertEqual(result, expected)

    def test_apply_query_parameters_invalid_column(self):
        """Test that invalid column raises HTTPException."""
        data = {"value": [{"id": "1", "name": "Test"}]}
        with self.assertRaises(HTTPException) as context:
            apply_query_parameters(data, {"invalid_column": "test"})
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn(
            "Query parameter 'invalid_column' does not match any column",
            str(context.exception.detail),
        )

    def test_apply_query_parameters_with_list_input(self):
        """Test filtering when input is a list instead of dict."""
        data = [
            {"id": "1", "status": "active"},
            {"id": "2", "status": "inactive"},
        ]
        result = apply_query_parameters(data, {"status": "active"})
        expected = [{"id": "1", "status": "active"}]
        self.assertEqual(result, expected)

    def test_apply_query_parameters_dict_without_value_key(self):
        """Test that dict without 'value' key returns unchanged."""
        data = {"some_other_key": "some_value", "metadata": "info"}
        result = apply_query_parameters(data, {"any": "filter"})
        self.assertEqual(result, data)

    def test_apply_query_parameters_non_dict_list_input(self):
        """Test that non-dict/list input returns unchanged (covers else case)."""
        # Test various non-dict/non-list types
        for data in ["string", 123, None, True]:
            result = apply_query_parameters(data, {"any": "filter"})
            self.assertEqual(result, data)
