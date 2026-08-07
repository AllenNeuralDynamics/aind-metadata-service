"""Tests methods in models module"""

import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from aind_slims_service_async_client.models import (
    SlimsHistologyData,
    SlimsSpimData,
)

from aind_metadata_service_server.models import (
    EcephysData,
    HealthCheck,
    HistologyData,
    MouseWeightData,
    SpimData,
)


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


class TestHistologyData(unittest.TestCase):
    """Tests for HistologyData"""

    def test_parse_protocol_id_html(self):
        """Tests parse_protocol_id method"""
        protocol_html = '<a href="https://example.com">Histology</a>'
        slims_hist = SlimsHistologyData(protocol_id=protocol_html)
        hist = HistologyData(**slims_hist.model_dump())
        self.assertEqual(hist.protocol_id, "https://example.com")

    def test_parse_protocol_id_malformed_html(self):
        """Tests parse_protocol_id method with malformed html"""
        protocol_html = "<a>Missing Href</a>"
        slims_hist = SlimsHistologyData(protocol_id=protocol_html)
        hist = HistologyData(**slims_hist.model_dump())
        self.assertIsNone(hist.protocol_id)

    def test_parse_protocol_id_non_html(self):
        """Tests parse_protocol_id method with non-html"""
        protocol_html = "Not in HTML"
        slims_hist = SlimsHistologyData(protocol_id=protocol_html)
        hist = HistologyData(**slims_hist.model_dump())
        self.assertEqual(hist.protocol_id, "Not in HTML")

    def test_parse_protocol_id_none(self):
        """Tests parse_protocol_id method with None"""
        slims_hist = SlimsHistologyData(protocol_id=None)
        hist = HistologyData(**slims_hist.model_dump())
        self.assertIsNone(hist.protocol_id)

    @patch("logging.warning")
    def test_parse_protocol_id_exception(self, mock_log_warn: MagicMock):
        """Tests parse_html when regular string passed in"""
        slims_hist = {"protocol_id": 123}
        hist = HistologyData(**slims_hist)
        self.assertIsNone(hist.protocol_id)
        mock_log_warn.assert_called_once()


class TestEcephysData(unittest.TestCase):
    """Tests for EcephysData"""

    def test_ecephys_data_with_stream_modules(self):
        """Tests EcephysData initialization with stream modules"""
        stream_module_dict = {
            "ccf_coordinate_unit": "&mu;m",
            "bregma_target_unit": "&mu;m",
            "surface_z_unit": "&mu;m",
            "manipulator_unit": "&mu;m",
        }
        ecephys_dict = {"stream_modules": [stream_module_dict]}
        parsed = EcephysData(**ecephys_dict)
        self.assertEqual(parsed.stream_modules[0].ccf_coordinate_unit, "μm")

    def test_ecephys_data_with_no_stream_modules(self):
        """Tests EcephysData initialization with no stream modules"""
        parsed = EcephysData(**{"stream_modules": None})
        self.assertIsNone(parsed.stream_modules)


class TestMouseWeightData(unittest.TestCase):
    """Tests for MouseWeightData"""

    def test_constructor_with_all_fields(self):
        """Test MouseWeightData constructor with all fields"""
        data = MouseWeightData(
            record_id="test-record-id",
            mouse_id="123456",
            weight=25.5,
            weight_datetime=datetime(2026, 8, 7, 17, 30, 14),
            is_baseline_weight=False,
            operator="Test Operator",
            workstation="TEST-STATION",
            software_version="1.0.0",
            software_source="WL",
            status="Active",
            notes="Test note",
        )

        self.assertEqual(data.record_id, "test-record-id")
        self.assertEqual(data.mouse_id, "123456")
        self.assertEqual(data.weight, 25.5)
        self.assertEqual(
            data.weight_datetime, datetime(2026, 8, 7, 17, 30, 14)
        )
        self.assertFalse(data.is_baseline_weight)
        self.assertEqual(data.operator, "Test Operator")
        self.assertEqual(data.workstation, "TEST-STATION")
        self.assertEqual(data.software_version, "1.0.0")
        self.assertEqual(data.software_source, "WL")
        self.assertEqual(data.status, "Active")
        self.assertEqual(data.notes, "Test note")

    def test_constructor_with_minimal_fields(self):
        """Test MouseWeightData constructor with only required fields (all optional)"""
        data = MouseWeightData()

        self.assertIsNone(data.record_id)
        self.assertIsNone(data.mouse_id)
        self.assertIsNone(data.weight)
        self.assertIsNone(data.weight_datetime)
        self.assertIsNone(data.is_baseline_weight)
        self.assertIsNone(data.operator)
        self.assertIsNone(data.workstation)
        self.assertIsNone(data.software_version)
        self.assertIsNone(data.software_source)
        self.assertIsNone(data.status)
        self.assertIsNone(data.notes)

    def test_constructor_with_partial_fields(self):
        """Test MouseWeightData constructor with some fields"""
        data = MouseWeightData(
            mouse_id="789012", weight=23.2, operator="Jane Doe"
        )

        self.assertEqual(data.mouse_id, "789012")
        self.assertEqual(data.weight, 23.2)
        self.assertEqual(data.operator, "Jane Doe")
        self.assertIsNone(data.record_id)
        self.assertIsNone(data.weight_datetime)

    def test_model_serialization(self):
        """Test that model can be serialized to dict"""
        data = MouseWeightData(
            record_id="test-id", mouse_id="123456", weight=25.5
        )

        serialized = data.model_dump()

        self.assertEqual(serialized["record_id"], "test-id")
        self.assertEqual(serialized["mouse_id"], "123456")
        self.assertEqual(serialized["weight"], 25.5)


if __name__ == "__main__":
    unittest.main()
