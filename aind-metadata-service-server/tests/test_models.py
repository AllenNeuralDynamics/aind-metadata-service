"""Tests methods in models module"""

import unittest
from unittest.mock import MagicMock, patch

from aind_slims_service_async_client.models import (
    SlimsSpimData,
    SlimsHistologyData
)
from aind_metadata_service_server.models import (
    HealthCheck,
    SpimData,
    HistologyData,
    EcephysStreamModuleData,
    EcephysData,
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
        protocol_html = '<a href="https://histology.com">Histology</a>'
        slims_hist = SlimsHistologyData(protocol_id=protocol_html)
        hist = HistologyData(**slims_hist.model_dump())
        self.assertEqual(hist.protocol_id, "https://histology.com")

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


class TestEcephysStreamModuleData(unittest.TestCase):
    """Tests for EcephysStreamModuleData"""

    def test_parse_micrometer_unit_html_entity(self):
        """Tests parsing of micrometer unit HTML entity"""
        data = {
            "ccf_coordinate_unit": "&mu;m",
            "bregma_target_unit": "&mu;m",
            "surface_z_unit": "&mu;m",
            "manipulator_unit": "&mu;m",
        }
        parsed = EcephysStreamModuleData(**data)
        self.assertEqual(parsed.ccf_coordinate_unit, "μm")
        self.assertEqual(parsed.bregma_target_unit, "μm")
        self.assertEqual(parsed.surface_z_unit, "μm")
        self.assertEqual(parsed.manipulator_unit, "μm")

    def test_parse_micrometer_unit_regular_string(self):
        """Tests parsing of micrometer unit regular string"""
        data = {
            "ccf_coordinate_unit": "mm",
            "bregma_target_unit": "mm",
            "surface_z_unit": "mm",
            "manipulator_unit": "mm",
        }
        parsed = EcephysStreamModuleData(**data)
        self.assertEqual(parsed.ccf_coordinate_unit, "mm")
        self.assertEqual(parsed.bregma_target_unit, "mm")
        self.assertEqual(parsed.surface_z_unit, "mm")
        self.assertEqual(parsed.manipulator_unit, "mm")


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
        ecephys_dict = {
            "stream_modules": [stream_module_dict]
        }
        parsed = EcephysData(**ecephys_dict)
        self.assertIsInstance(
            parsed.stream_modules[0], EcephysStreamModuleData
        )
        self.assertEqual(parsed.stream_modules[0].ccf_coordinate_unit, "μm")

    def test_ecephys_data_with_no_stream_modules(self):
        """Tests EcephysData initialization with no stream modules"""
        parsed = EcephysData()
        self.assertIsNone(parsed.stream_modules)


if __name__ == "__main__":
    unittest.main()
