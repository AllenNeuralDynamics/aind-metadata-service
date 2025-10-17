"""Module to test ProtocolMapper class"""

import unittest

from aind_smartsheet_service_async_client.models import ProtocolsModel

from aind_metadata_service_server.mappers.protocol import ProtocolMapper
from aind_metadata_service_server.models import ProtocolInformation


class TestProtocolMapper(unittest.TestCase):
    """Class to test methods for ProtocolMapper."""

    def setUp(self):
        """Set up test data."""
        self.protocols_sheet = [
            ProtocolsModel(
                protocol_type="Specimen Procedures",
                procedure_name="Delipidation",
                protocol_name=(
                    "Tetrahydrofuran and Dichloromethane Delipidation of a "
                    "Whole Mouse Brain"
                ),
                doi="dx.doi.org/10.17504/protocols.io.36wgqj1kxvk5/v1",
                version="1.0",
            ),
            ProtocolsModel(
                protocol_type=None,
                procedure_name=None,
                protocol_name=None,
                doi=None,
                version=None,
                protocol_collection=None,
            ),
        ]

    def test_mapping_success(self):
        """Tests successful mapping of delipidation protocol data"""
        mapper = ProtocolMapper(smartsheet_protocol=self.protocols_sheet[0])
        protocol_info = mapper.map_to_protocol_information()

        expected_protocol = ProtocolInformation(
            protocol_type="Specimen Procedures",
            procedure_name="Delipidation",
            protocol_name=(
                "Tetrahydrofuran and Dichloromethane Delipidation of a "
                "Whole Mouse Brain"
            ),
            doi="dx.doi.org/10.17504/protocols.io.36wgqj1kxvk5/v1",
            version="1.0",
            protocol_collection=None,
        )

        self.assertEqual(expected_protocol, protocol_info)

    def test_mapping_with_none_values(self):
        """Tests mapping when protocol model has explicitly None fields"""
        mapper = ProtocolMapper(smartsheet_protocol=self.protocols_sheet[1])
        protocol_info = mapper.map_to_protocol_information()

        self.assertIsNone(protocol_info)

    def test_mapping_with_validation_error(self):
        """Tests mapping when validation errors occur (uses model_construct)"""
        problematic_protocol = ProtocolsModel(
            protocol_type=None,
            procedure_name="Test Procedure",
            protocol_name="Test Protocol",
            doi="invalid_doi_format",
            version=None,
            protocol_collection=None,
        )
        mapper = ProtocolMapper(smartsheet_protocol=problematic_protocol)
        protocol_info = mapper.map_to_protocol_information()
        self.assertIsInstance(protocol_info, ProtocolInformation)


if __name__ == "__main__":
    unittest.main()
