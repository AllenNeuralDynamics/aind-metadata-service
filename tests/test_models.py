"""Tests methods in models module."""

import unittest

from aind_metadata_service.models import ProtocolInformation


class TestProtocolInformation(unittest.TestCase):
    """Test methods in ProtocolInformation class"""

    def test_validation_checks(self):
        """Tests that floats and None get converted correctly."""
        protocol_info1 = ProtocolInformation(
            protocol_type="some_type",
            procedure_name="some_procedure",
            protocol_name="some_name",
            doi="some_doi",
            version=4.0,
            protocol_collection=None,
        )
        self.assertEqual("some_type", protocol_info1.protocol_type)
        self.assertEqual("some_procedure", protocol_info1.procedure_name)
        self.assertEqual("some_name", protocol_info1.protocol_name)
        self.assertEqual("some_doi", protocol_info1.doi)
        self.assertEqual("4.0", protocol_info1.version)
        self.assertIsNone(protocol_info1.protocol_collection)


if __name__ == "__main__":
    unittest.main()
