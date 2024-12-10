"""Tests handler module"""

import json
import os
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from requests import Response

from aind_metadata_service.backends.tars.configs import Settings
from aind_metadata_service.backends.tars.handler import SessionHandler
from aind_metadata_service.backends.tars.models import (
    Alias,
    MoleculeData,
    MoleculeResponse,
    MoleculeType,
    PrepLotData,
    PrepLotResponse,
    Species,
    TargetedCellPopulation,
    TargetedRoi,
    Titers,
    ViralPrep,
    ViralPrepType,
    Virus,
)

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".."
RESOURCE_DIR = TEST_DIR / "resources" / "backends" / "tars"


class TestSessionHandler(unittest.TestCase):
    """Test methods in SessionHandler Class"""

    @classmethod
    def setUpClass(cls):
        """Sets up class with by preloading json resources"""

        with open(RESOURCE_DIR / "raw_prep_lot_response.json", "r") as f:
            raw_prep_lot_response_json = json.load(f)

        with open(RESOURCE_DIR / "raw_molecules_response.json", "r") as f:
            raw_molecules_response_json = json.load(f)

        example_settings = Settings(
            tenant_id="123-abc",
            client_id="456-def",
            client_secret="my_secret",
            scope="www.scope.example.com",
            resource="www.res.example.com",
        )
        mock_good_prep_lot_response = Response()
        mock_good_prep_lot_response.status_code = 200
        mock_good_prep_lot_response._content = json.dumps(
            raw_prep_lot_response_json
        ).encode("utf-8")
        mock_good_molecules_response = Response()
        mock_good_molecules_response.status_code = 200
        mock_good_molecules_response._content = json.dumps(
            raw_molecules_response_json
        ).encode("utf-8")
        cls.example_settings = example_settings
        cls.raw_prep_lot_response_json = raw_prep_lot_response_json
        cls.raw_molecules_response_json = raw_molecules_response_json
        cls.raw_prep_lot_response = mock_good_prep_lot_response
        cls.raw_molecules_response = mock_good_molecules_response
        cls.expected_prep_lot_response = PrepLotResponse(
            data=[
                PrepLotData(
                    createdAt=datetime(
                        2023, 10, 19, 22, 22, 32, 417498, tzinfo=timezone.utc
                    ),
                    updatedAt=datetime(
                        2024, 7, 29, 21, 28, 20, 65665, tzinfo=timezone.utc
                    ),
                    createdBy="person.two@example.com",
                    updatedBy="person.three@example.com",
                    id="634bc378-b5ad-4079-8552-968b084490ba",
                    lot="VT3214g",
                    datePrepped=datetime(
                        2023, 2, 4, 0, 0, tzinfo=timezone.utc
                    ),
                    viralPrep=ViralPrep(
                        createdAt=datetime(
                            2023,
                            10,
                            19,
                            22,
                            22,
                            32,
                            417498,
                            tzinfo=timezone.utc,
                        ),
                        updatedAt=datetime(
                            2024,
                            7,
                            29,
                            21,
                            28,
                            19,
                            942782,
                            tzinfo=timezone.utc,
                        ),
                        createdBy="person.two@example.com",
                        updatedBy="person.three@example.com",
                        id="85bbb563-f007-479c-831a-984199f7797c",
                        rrId=None,
                        viralPrepType=ViralPrepType(
                            createdAt=datetime(
                                2021,
                                8,
                                20,
                                23,
                                41,
                                37,
                                183718,
                                tzinfo=timezone.utc,
                            ),
                            updatedAt=None,
                            createdBy="person.one@example.com",
                            updatedBy=None,
                            id="f948a36e-1518-4a4b-b021-ae54ea7f4d37",
                            name="Purified-SOP#VC003",
                        ),
                        virus=Virus(
                            createdAt=datetime(
                                2023,
                                10,
                                19,
                                22,
                                22,
                                32,
                                573821,
                                tzinfo=timezone.utc,
                            ),
                            updatedAt=datetime(
                                2024,
                                7,
                                29,
                                21,
                                28,
                                19,
                                866687,
                                tzinfo=timezone.utc,
                            ),
                            createdBy="person.two@example.com",
                            updatedBy="person.three@example.com",
                            id="9ac86fd0-0907-4ccd-98c6-2eff07e13cb2",
                            rrId=None,
                            aliases=[
                                Alias(
                                    createdAt=datetime(
                                        2023,
                                        10,
                                        19,
                                        22,
                                        22,
                                        32,
                                        573824,
                                        tzinfo=timezone.utc,
                                    ),
                                    updatedAt=datetime(
                                        2024,
                                        7,
                                        29,
                                        21,
                                        28,
                                        19,
                                        866687,
                                        tzinfo=timezone.utc,
                                    ),
                                    createdBy="person.two@example.com",
                                    updatedBy="person.three@example.com",
                                    id="2df4b32c-5baf-434c-bf88-ebace7ebed3b",
                                    citation=None,
                                    isPreferred=True,
                                    name="AiV300024",
                                ),
                                Alias(
                                    createdAt=datetime(
                                        2024,
                                        1,
                                        23,
                                        20,
                                        24,
                                        53,
                                        588652,
                                        tzinfo=timezone.utc,
                                    ),
                                    updatedAt=datetime(
                                        2024,
                                        7,
                                        29,
                                        21,
                                        28,
                                        19,
                                        866687,
                                        tzinfo=timezone.utc,
                                    ),
                                    createdBy="person.two@example.com",
                                    updatedBy="person.three@example.com",
                                    id="965d8d74-4ae5-4fe6-a8b0-34db4d01bf9c",
                                    citation=None,
                                    isPreferred=False,
                                    name="pAAV-Syn-Flex-TREx2-tTA",
                                ),
                            ],
                            capsid=None,
                            citations=[],
                            molecules=[],
                            otherMolecules=[],
                            patents=[],
                        ),
                        citations=[],
                        shipments=[],
                        patents=[],
                        materialTransferAgreements=[],
                        qcCertificationFiles=[],
                        serotypes=[],
                    ),
                    titers=[
                        Titers(
                            createdAt=datetime(
                                2023,
                                10,
                                19,
                                22,
                                23,
                                48,
                                925791,
                                tzinfo=timezone.utc,
                            ),
                            updatedAt=datetime(
                                2024,
                                7,
                                29,
                                21,
                                28,
                                20,
                                65665,
                                tzinfo=timezone.utc,
                            ),
                            createdBy="person.two@example.com",
                            updatedBy="person.three@example.com",
                            id="b8aa1cd3-5bb6-43f7-be94-eb4cf4858235",
                            notes="",
                            isPreferred=True,
                            thawedCount=1,
                            result=41300000000000,
                            titerType=None,
                        )
                    ],
                )
            ],
            totalCount=1,
            pageSize=1,
            page=0,
            orderBy="id",
            order="1",
            morePages=True,
            search="VT3214g",
            searchFields="lot",
        )
        cls.expected_molecule_response = MoleculeResponse(
            data=[
                MoleculeData(
                    createdAt=datetime(
                        2023, 3, 3, 5, 19, 0, 949949, tzinfo=timezone.utc
                    ),
                    updatedAt=datetime(
                        2024, 11, 14, 2, 46, 46, 960826, tzinfo=timezone.utc
                    ),
                    createdBy="person.two@example.com",
                    updatedBy="person.two@example.com",
                    id="d30ed9f0-27e5-446a-aa84-f8de3c1150cb",
                    moleculeType=MoleculeType(
                        createdAt=datetime(
                            2021,
                            1,
                            14,
                            10,
                            38,
                            10,
                            534000,
                            tzinfo=timezone.utc,
                        ),
                        updatedAt=None,
                        createdBy="System",
                        updatedBy=None,
                        id="2cbd1e06-035d-4290-902c-50b3ced964e8",
                        name="Plasmid (DNA)",
                    ),
                    state=None,
                    aliases=[
                        Alias(
                            createdAt=datetime(
                                2024,
                                7,
                                19,
                                2,
                                50,
                                18,
                                403244,
                                tzinfo=timezone.utc,
                            ),
                            updatedAt=datetime(
                                2024,
                                11,
                                14,
                                2,
                                48,
                                1,
                                504357,
                                tzinfo=timezone.utc,
                            ),
                            createdBy="person.two@example.com",
                            updatedBy="person.two@example.com",
                            id="2547b416-64c6-442a-9ebc-08de4d57414a",
                            citation=None,
                            isPreferred=False,
                            name="pAAV-MGT_E12-minGprom-FlpO-WPRE-hGHpA",
                        ),
                        Alias(
                            createdAt=datetime(
                                2023,
                                3,
                                3,
                                5,
                                19,
                                1,
                                69687,
                                tzinfo=timezone.utc,
                            ),
                            updatedAt=datetime(
                                2024,
                                11,
                                14,
                                2,
                                48,
                                1,
                                504353,
                                tzinfo=timezone.utc,
                            ),
                            createdBy="person.two@example.com",
                            updatedBy="person.two@example.com",
                            id="6dac377d-1085-4a57-8cca-1dd0814d305a",
                            citation=None,
                            isPreferred=True,
                            name="AiP1109",
                        ),
                    ],
                    citations=[],
                    rrId=None,
                    fullName="pAAV-AiE2012m-minG-FlpO-WPRE-HGHpA",
                    addgeneId=None,
                    mgiId=None,
                    notes=None,
                    sequence=(
                        "CATG"
                    ),
                    genes=[],
                    loci=[],
                    species=[
                        Species(
                            createdAt=datetime(
                                2021,
                                8,
                                20,
                                12,
                                14,
                                56,
                                208931,
                                tzinfo=timezone.utc,
                            ),
                            updatedAt=None,
                            createdBy="System",
                            updatedBy=None,
                            id="e5384ac0-0385-4a2e-8caa-c5eb0142813e",
                            rorID=None,
                            name="synthetic construct",
                        )
                    ],
                    organizations=[],
                    shipments=[],
                    materialTransferAgreements=[],
                    genBankFiles=["de25d8b6-bb2a-4d04-a790-ef3d164cbe35"],
                    mapFiles=["418390ca-bc97-4b84-ab28-915668406b20"],
                    fastaFiles=["8f9e2880-3d22-4368-8c8f-c4b30ab6b035"],
                    parents=[],
                    children=[],
                    patents=[],
                    creators=[],
                    principalInvestigator=None,
                    targetedCellPopulations=[
                        TargetedCellPopulation(
                            createdAt=datetime(
                                2022,
                                4,
                                20,
                                21,
                                55,
                                22,
                                780516,
                                tzinfo=timezone.utc,
                            ),
                            updatedAt=None,
                            createdBy="person.two@example.com",
                            updatedBy=None,
                            id="6e3f839e-1a6c-4557-ae1c-99d7212ba1fb",
                            name="L6_IT_Car3",
                        )
                    ],
                    validatedCellPopulations=[],
                    targetedRois=[
                        TargetedRoi(
                            createdAt=datetime(
                                2022,
                                6,
                                8,
                                22,
                                26,
                                43,
                                972576,
                                tzinfo=timezone.utc,
                            ),
                            updatedAt=None,
                            createdBy="person.one@example.com",
                            updatedBy=None,
                            id="94d8b2cb-2a64-4fd8-b07c-f4dc8ed199ea",
                            name="CTX",
                        )
                    ],
                    validatedRois=[],
                    genomeCoordinates=None,
                )
            ],
            totalCount=1,
            pageSize=50,
            page=0,
            orderBy="id",
            order="1",
            morePages=False,
            search="AiP1109",
            searchFields="name",
        )

    def test_sanitize_input(self):
        """Tests _sanitize_input method strips whitespaces"""

        output_str = SessionHandler._sanitize_input(" ABC123\t\n")
        self.assertEqual("ABC123", output_str)

    @patch("requests.Session")
    def test_get_raw_prep_lot_response(self, mock_session: MagicMock):
        """Tests _get_raw_prep_lot_response"""
        mock_session.get.return_value = self.raw_prep_lot_response
        handler = SessionHandler(
            session=mock_session,
            bearer_token="abc-123",
            settings=self.example_settings,
        )

        response = handler._get_raw_prep_lot_response(
            prep_lot_id="VT3214g", page_size=1
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(self.raw_prep_lot_response_json, response.json())
        mock_session.assert_has_calls(
            [
                call.headers.update({"Authorization": "Bearer abc-123"}),
                call.get(
                    url="www.res.example.com/api/v1/ViralPrepLots",
                    params={
                        "pageSize": "1",
                        "order": "1",
                        "orderBy": "id",
                        "searchFields": "lot",
                        "search": "VT3214g",
                    },
                ),
            ]
        )

    @patch("requests.Session")
    def test_get_prep_lot_response(self, mock_session: MagicMock):
        """Tests _get_prep_lot_response method when 200 response returned"""
        mock_session.get.return_value = self.raw_prep_lot_response
        handler = SessionHandler(
            session=mock_session,
            bearer_token="abc-123",
            settings=self.example_settings,
        )
        response = handler._get_prep_lot_response(prep_lot_id="VT3214g")
        self.assertEqual(self.expected_prep_lot_response, response)

    @patch("requests.Session")
    def test_get_prep_lot_response_error(self, mock_session: MagicMock):
        """Tests get_prep_lot_response method when 500 response returned"""
        mock_response = Response()
        mock_response.status_code = 500
        mock_session.get.return_value = mock_response
        handler = SessionHandler(
            session=mock_session,
            bearer_token="abc-123",
            settings=self.example_settings,
        )
        with self.assertRaises(Exception) as e:
            handler._get_prep_lot_response(prep_lot_id="VT3214g ")

        self.assertIn("500 Server Error", e.exception.args[0])

    @patch("requests.Session")
    def test_get_prep_lot_data(self, mock_session: MagicMock):
        """Tests _get_prep_lot_data method"""
        mock_session.get.return_value = self.raw_prep_lot_response
        handler = SessionHandler(
            session=mock_session,
            bearer_token="abc-123",
            settings=self.example_settings,
        )
        data = handler.get_prep_lot_data(prep_lot_id="VT3214g")
        expected_data = self.expected_prep_lot_response.data
        self.assertEqual(expected_data, data)

    @patch("requests.Session")
    def test_get_raw_molecules_response(self, mock_session: MagicMock):
        """Tests _get_raw_molecules_response"""
        mock_session.get.return_value = self.raw_molecules_response
        handler = SessionHandler(
            session=mock_session,
            bearer_token="abc-123",
            settings=self.example_settings,
        )
        response = handler._get_raw_molecules_response(plasmid_name="AiP1109")

        self.assertEqual(200, response.status_code)
        self.assertEqual(self.raw_molecules_response_json, response.json())

    @patch("requests.Session")
    def test_get_molecules_response(self, mock_session: MagicMock):
        """Tests get_molecules_response"""
        mock_session.get.return_value = self.raw_molecules_response
        handler = SessionHandler(
            session=mock_session,
            bearer_token="abc-123",
            settings=self.example_settings,
        )
        response = handler._get_molecule_response(plasmid_name="AiP1109")
        self.assertEqual(self.expected_molecule_response, response)

    @patch("requests.Session")
    def test_get_molecule_data(self, mock_session: MagicMock):
        """Tests _get_prep_lot_data method"""
        mock_session.get.return_value = self.raw_molecules_response
        handler = SessionHandler(
            session=mock_session,
            bearer_token="abc-123",
            settings=self.example_settings,
        )
        data = handler.get_molecule_data(plasmid_name="AiP1109")
        expected_data = self.expected_molecule_response.data
        self.assertEqual(expected_data, data)


if __name__ == "__main__":
    unittest.main()
