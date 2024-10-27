"""Tests validators in models module"""

import unittest
from datetime import date
from decimal import Decimal

from aind_metadata_service.backends.smartsheet.models import (
    FundingModel,
    PerfusionsModel,
    ProtocolsModel,
)


class TestFunding(unittest.TestCase):
    """Tests Funding Model"""

    def test_model_construction(self):
        """Tests basic model construction"""

        funding_model = FundingModel(
            project_name="v1omFISH",
            project_code="121-01-010-10",
            funding_institution="Allen Institute",
            grant_number=None,
            investigators="person.one@acme.org, Person Two",
        )
        self.assertEqual("v1omFISH", funding_model.project_name)
        self.assertEqual("121-01-010-10", funding_model.project_code)
        self.assertEqual("Allen Institute", funding_model.funding_institution)
        self.assertIsNone(funding_model.grant_number)
        self.assertEqual(
            "person.one@acme.org, Person Two", funding_model.investigators
        )


class TestPerfusions(unittest.TestCase):
    """Tests Perfusions Model"""

    def test_model_construction(self):
        """Tests basic model construction"""

        example_iacuc_protocol = (
            "2109 - Analysis of brain - wide neural circuits in the mouse"
        )

        perfusions_model = PerfusionsModel(
            subject_id="689418",
            date="2023-10-02",
            experimenter="Person One",
            iacuc_protocol=example_iacuc_protocol,
            animal_weight_prior="22",
            output_specimen_id="689418",
            postfix_solution="1xPBS",
            notes="Good",
        )

        self.assertEqual(Decimal("689418"), perfusions_model.subject_id)
        self.assertEqual(date(2023, 10, 2), perfusions_model.date)
        self.assertEqual("Person One", perfusions_model.experimenter)
        self.assertEqual(
            example_iacuc_protocol, perfusions_model.iacuc_protocol
        )
        self.assertEqual(Decimal("22"), perfusions_model.animal_weight_prior)
        self.assertEqual(
            Decimal("689418"), perfusions_model.output_specimen_id
        )
        self.assertEqual("1xPBS", perfusions_model.postfix_solution)
        self.assertEqual("Good", perfusions_model.notes)


class TestProtocols(unittest.TestCase):
    """Tests Protocols Model"""

    def test_model_construction(self):
        """Tests basic model construction"""

        example_protocol_name = (
            "Tetrahydrofuran and Dichloromethane Delipidation of a Whole "
            "Mouse Brain"
        )
        protocols_model = ProtocolsModel(
            protocol_type="Specimen Procedures",
            procedure_name="Delipidation",
            protocol_name=example_protocol_name,
            doi="dx.doi.org/10.17504/protocols.io.36wgqj1kxvk5/v1",
            version="1.0",
        )

        self.assertEqual("Specimen Procedures", protocols_model.protocol_type)
        self.assertEqual("Delipidation", protocols_model.procedure_name)
        self.assertEqual(example_protocol_name, protocols_model.protocol_name)
        self.assertEqual(
            "dx.doi.org/10.17504/protocols.io.36wgqj1kxvk5/v1",
            protocols_model.doi,
        )
        self.assertEqual(Decimal("1.0"), protocols_model.version)


if __name__ == "__main__":
    unittest.main()
