"""Module to test ProtocolMapper class"""

import unittest
from decimal import Decimal

from aind_smartsheet_service_async_client.models import ProtocolsModel

from aind_metadata_service_server.models import ProtocolInformation
from aind_metadata_service_server.mappers.protocol import ProtocolMapper


class TestProtocolMapper(unittest.TestCase):
    """Class to test methods for ProtocolMapper."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        cls.protocols_sheet = [
            ProtocolsModel(
                protocol_type="Specimen Procedures",
                procedure_name="Immunolabeling",
                protocol_name="Immunolabeling of a Whole Mouse Brain",
                doi="dx.doi.org/10.17504/protocols.io.ewov1okwylr2/v1",
                version="1.0",
            ),
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
                protocol_type="Specimen Procedures",
                procedure_name="Delipidation",
                protocol_name=(
                    "Aqueous (SBiP) Delipidation of a Whole Mouse Brain"
                ),
                doi="dx.doi.org/10.17504/protocols.io.n2bvj81mwgk5/v1",
                version="1.0",
            ),
            ProtocolsModel(
                protocol_type="Specimen Procedures",
                procedure_name="Gelation + previous steps",
                protocol_name=(
                    "Whole Mouse Brain Delipidation, Immunolabeling, and "
                    "Expansion Microscopy"
                ),
                doi="dx.doi.org/10.17504/protocols.io.n92ldpwjxl5b/v1",
                version="1.0",
                protocol_collection=False,
            ),
            ProtocolsModel(
                protocol_type="Surgical Procedures",
                procedure_name="Injection Nanoject",
                protocol_name="Injection of Viral Tracers by Nanoject V.4",
                doi="dx.doi.org/10.17504/protocols.io.bp2l6nr7kgqe/v4",
                version="4.0",
            ),
            ProtocolsModel(
                protocol_type="Surgical Procedures",
                procedure_name="Injection Iontophoresis",
                protocol_name=(
                    "Stereotaxic Surgery for Delivery of Tracers by "
                    "Iontophoresis V.3"
                ),
                doi="dx.doi.org/10.17504/protocols.io.bgpvjvn6",
                version="3.0",
            ),
            ProtocolsModel(
                protocol_type="Surgical Procedures",
                procedure_name="Perfusion",
                protocol_name=(
                    "Mouse Cardiac Perfusion Fixation and Brain "
                    "Collection V.5"
                ),
                doi="dx.doi.org/10.17504/protocols.io.bg5vjy66",
                version="5.0",
            ),
            ProtocolsModel(
                protocol_type="Imaging Techniques",
                procedure_name="SmartSPIM Imaging",
                protocol_name="Imaging cleared mouse brains on SmartSPIM",
                doi="dx.doi.org/10.17504/protocols.io.3byl4jo1rlo5/v1",
                version="1.0",
            ),
            ProtocolsModel(
                protocol_type="Imaging Techniques",
                procedure_name="SmartSPIM setup",
                protocol_name="SmartSPIM setup and alignment",
                doi="dx.doi.org/10.17504/protocols.io.5jyl8jyb7g2w/v1",
                version="1.0",
            ),
            ProtocolsModel(),
            ProtocolsModel(
                protocol_type=None,
                procedure_name=None,
                protocol_name=None,
                doi=None,
                version=None,
                protocol_collection=None,
            ),
        ]

    def test_mapping_success_immunolabeling(self):
        """Tests successful mapping of immunolabeling protocol data"""
        mapper = ProtocolMapper(smartsheet_protocol=self.protocols_sheet[0])
        protocol_info = mapper.map_to_protocol_information()

        expected_protocol = ProtocolInformation(
            protocol_type="Specimen Procedures",
            procedure_name="Immunolabeling",
            protocol_name="Immunolabeling of a Whole Mouse Brain",
            doi="dx.doi.org/10.17504/protocols.io.ewov1okwylr2/v1",
            version="1.0",
            protocol_collection=None,
        )

        self.assertEqual(
            expected_protocol.protocol_type, protocol_info.protocol_type
        )
        self.assertEqual(
            expected_protocol.procedure_name, protocol_info.procedure_name
        )
        self.assertEqual(
            expected_protocol.protocol_name, protocol_info.protocol_name
        )
        self.assertEqual(expected_protocol.doi, protocol_info.doi)
        self.assertEqual(expected_protocol.version, protocol_info.version)

    def test_mapping_success_delipidation(self):
        """Tests successful mapping of delipidation protocol data"""
        mapper = ProtocolMapper(smartsheet_protocol=self.protocols_sheet[1])
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
        mapper = ProtocolMapper(smartsheet_protocol=self.protocols_sheet[10])
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