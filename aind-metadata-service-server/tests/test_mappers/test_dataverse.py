"""Module to test dataverse mapper"""

import unittest

from aind_metadata_service_server.mappers.dataverse import (
    _filter_dataverse_metadata,
)


class TestDataverseMapper(unittest.TestCase):
    """Class to test methods for Dataverse mapper."""

    def test_filter_removes_metadata_keys(self):
        """Test that metadata keys are removed from the data."""
        data = {
            "@data.etag": "some-etag",
            "_private": "some-private-data",
            "statecode@OData": "some-state",
            "data": "some-data",
            "nested": {
                "@meta": "some-meta",
                "keep": 123,
                "_hidden": "some-hidden",
            },
            "list": [{"bar@Odata": 2, "bar": 2}, {"_foo": 4, "foo": 4}],
        }
        filtered = _filter_dataverse_metadata(data)
        self.assertNotIn("@data.etag", filtered)
        self.assertNotIn("_private", filtered)
        self.assertNotIn("statecode@OData", filtered)
        self.assertEqual(filtered["data"], "some-data")
        self.assertNotIn("@meta", filtered["nested"])
        self.assertNotIn("_hidden", filtered["nested"])
        self.assertEqual(filtered["nested"]["keep"], 123)
        self.assertEqual(filtered["list"], [{"bar": 2}, {"foo": 4}])
