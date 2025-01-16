"""Tests client package"""

import json
import os
import unittest
from unittest.mock import MagicMock, patch

from requests import Response

from aind_metadata_service.mgi.client import MgiClient, MgiSettings


class TestMgiSettings(unittest.TestCase):
    """Class to test methods for MgiSettings."""

    EXAMPLE_ENV_VAR1 = {"MGI_URL": "http://www.example.com/"}

    @patch.dict(os.environ, EXAMPLE_ENV_VAR1, clear=True)
    def test_model_construct(self):
        """Tests that model is constructed from env vars"""

        settings = MgiSettings()
        self.assertEqual(
            "http://www.example.com/", settings.url.unicode_string()
        )


class TestMgiClient(unittest.TestCase):
    """Class to test methods for MgiClient"""

    @classmethod
    def setUpClass(cls):
        """Set up class with examples."""

        example_response = Response()
        example_response.status_code = 200
        example_response._content = json.dumps(
            {
                "summaryRows": [
                    {
                        "detailUri": "/allele/MGI:5558086",
                        "featureType": "Targeted allele",
                        "strand": None,
                        "chromosome": "9",
                        "stars": "****",
                        "bestMatchText": "Ai93",
                        "bestMatchType": "Synonym",
                        "name": (
                            "intergenic site 7; "
                            "targeted mutation 93, Hongkui Zeng"
                        ),
                        "location": "syntenic",
                        "symbol": "Igs7<tm93.1(tetO-GCaMP6f)Hze>",
                    }
                ],
                "totalCount": 1,
                "meta": None,
            }
        ).encode("utf-8")
        cls.example_response = example_response
        settings = MgiSettings(url="http://www.example.com")
        cls.example_client = MgiClient(settings=settings)

    def test_get_allele_names_from_genotype(self):
        """Tests get_allele_names_from_genotype"""

        genotype = "Pvalb-IRES-Cre/wt;RCL-somBiPoles_mCerulean-WPRE/wt"
        allele_names = self.example_client.get_allele_names_from_genotype(
            genotype=genotype
        )
        expected_allele_names = [
            "Pvalb-IRES-Cre",
            "RCL-somBiPoles_mCerulean-WPRE",
        ]
        self.assertEqual(expected_allele_names, allele_names)

    def test_get_allele_names_from_genotype_none(self):
        """Tests get_allele_names_from_genotype when genotype is None"""

        genotype = None
        allele_names = self.example_client.get_allele_names_from_genotype(
            genotype=genotype
        )
        expected_allele_names = []
        self.assertEqual(expected_allele_names, allele_names)

    @patch("requests.get")
    def test_get_allele_info(self, mock_get: MagicMock):
        """Tests get_allele_info method"""

        mock_get.return_value = self.example_response
        response = self.example_client.get_allele_info(allele_name="Ai93")
        expected_symbol = "Igs7<tm93.1(tetO-GCaMP6f)Hze>"
        self.assertEqual(expected_symbol, response.summaryRows[0].symbol)

    @patch("requests.get")
    def test_get_allele_info_error(self, mock_get: MagicMock):
        """Tests get_allele_info method when there is a server error"""

        mock_get.side_effect = Exception("Something went wrong.")
        with self.assertLogs(level="ERROR") as captured:
            response = self.example_client.get_allele_info(allele_name="Ai93")
        self.assertIn("Something went wrong.", captured.output[0])
        self.assertEqual(500, response.status_code.value)


if __name__ == "__main__":
    unittest.main()
