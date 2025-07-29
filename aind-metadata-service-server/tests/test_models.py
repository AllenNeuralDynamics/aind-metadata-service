"""Tests methods in models module"""

import unittest
from unittest.mock import MagicMock, patch

from aind_slims_service_async_client.models.slims_spim_data import (
    SlimsSpimData,
)

from aind_metadata_service_server.models import HealthCheck, SpimData


class TestHealthCheck(unittest.TestCase):
    """Tests for HealthCheck class"""

    def test_constructor(self):
        """Basic test for class constructor"""

        health_check = HealthCheck()
        self.assertEqual("OK", health_check.status)


class TestSpimData(unittest.TestCase):
    """Tests for SpimData"""

    def test_parse_protocol_id(self):
        """Tests parse_protocol_id method"""
        protocol_html = '<a href="https://example.com">Example</a>'
        slims_spim_data = SlimsSpimData(protocol_id=protocol_html)
        spim_data = SpimData(**slims_spim_data.model_dump())
        self.assertEqual("https://example.com", spim_data.protocol_id)

    def test_parse_protocol_id_malformed_html(self):
        """Tests parse_protocol_id method with malformed html"""
        protocol_html = "<a>Missing Href</a>"
        slims_spim_data = SlimsSpimData(protocol_id=protocol_html)
        spim_data = SpimData(**slims_spim_data.model_dump())
        self.assertIsNone(spim_data.protocol_id)

    def test_parse_protocol_id_non_html(self):
        """Tests parse_protocol_id method with non-html"""
        protocol_html = "Not in HTML"
        slims_spim_data = SlimsSpimData(protocol_id=protocol_html)
        spim_data = SpimData(**slims_spim_data.model_dump())
        self.assertEqual("Not in HTML", spim_data.protocol_id)

    def test_parse_protocol_id_none(self):
        """Tests parse_protocol_id method with None"""
        slims_spim_data = SlimsSpimData(protocol_id=None)
        spim_data = SpimData(**slims_spim_data.model_dump())
        self.assertIsNone(spim_data.protocol_id)

    @patch("logging.warning")
    def test_parse_error(self, mock_log_warn: MagicMock):
        """Tests parse_html when regular string passed in"""
        slims_spim_data = {"protocol_id": 123}
        spim_data = SpimData(**slims_spim_data)
        self.assertIsNone(spim_data.protocol_id)
        mock_log_warn.assert_called_once()


if __name__ == "__main__":
    unittest.main()
