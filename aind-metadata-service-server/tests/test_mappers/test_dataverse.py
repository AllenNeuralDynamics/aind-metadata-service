"""Module to test dataverse mapper"""

import unittest

from aind_metadata_service_server.mappers.dataverse import (
    filter_dataverse_metadata,
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
