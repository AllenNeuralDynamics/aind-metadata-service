"""Tests methods in models module"""

import unittest
from datetime import datetime

from aind_metadata_service_server.models import (
    HealthCheck,
    MouseWeightData,
)


class TestHealthCheck(unittest.TestCase):
    """Tests for HealthCheck class"""

    def test_constructor(self):
        """Basic test for class constructor"""

        health_check = HealthCheck()
        self.assertEqual("OK", health_check.status)


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
