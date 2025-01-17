"""Module to test Smartsheet client class"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from aind_data_schema.core.procedures import (
    Craniotomy,
    Headframe,
    IontophoresisInjection,
    NanojectInjection,
    Perfusion,
    Procedures,
    ProtectiveMaterial,
    Surgery,
)
from pydantic import ValidationError

from aind_metadata_service.client import StatusCodes
from aind_metadata_service.models import ProtocolInformation
from aind_metadata_service.response_handler import ModelResponse
from aind_metadata_service.smartsheet.client import (
    SmartSheetClient,
    SmartsheetSettings,
)
from aind_metadata_service.smartsheet.protocols.mapping import (
    ProtocolsIntegrator,
    ProtocolsMapper,
)
from aind_metadata_service.smartsheet.protocols.models import ProtocolNames

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".."
EXAMPLE_PATH = (
    TEST_DIR / "resources" / "smartsheet" / "test_protocols_sheet.json"
)


class TestSmartsheetProtocolsClient(unittest.TestCase):
    """Class to test methods for SmartsheetClient."""

    @classmethod
    def setUpClass(cls):
        """Load json files before running tests."""
        with open(EXAMPLE_PATH, "r") as f:
            contents = json.load(f)
        cls.example_sheet = json.dumps(contents)
        cls.protocols_integrator = ProtocolsIntegrator()
        cls.nano_name = "Injection of Viral Tracers by Nanoject V.4"
        cls.surgery_name = (
            "General Set-Up and Take-Down for Rodent Neurosurgery"
        )

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_get_sheet_success(self, mock_get_sheet: MagicMock):
        """Tests successful sheet return response"""
        mock_get_sheet.return_value.to_json.return_value = self.example_sheet
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=7478444220698500
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        sheet_response = client.get_sheet()
        sheet_str = json.loads(sheet_response.body)["data"]
        sheet = json.loads(sheet_str)
        self.assertEqual("Published Protocols", sheet["name"])
        self.assertEqual(7478444220698500, sheet["id"])
        self.assertEqual(26, sheet["version"])
        self.assertEqual(13, sheet["totalRowCount"])

    @patch("smartsheet.sheets.Sheets.get_sheet")
    @patch("logging.error")
    def test_get_sheet_error(
        self, mock_log_error: MagicMock, mock_get_sheet: MagicMock
    ):
        """Tests sheet return error response"""
        mock_get_sheet.side_effect = MagicMock(
            side_effect=Exception("Error connecting to server")
        )
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=7478444220698500
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        response = client.get_sheet()
        self.assertEqual(500, response.status_code)
        self.assertEqual(
            "Error connecting to server", json.loads(response.body)["message"]
        )
        mock_log_error.assert_called_once_with(
            "Exception('Error connecting to server',)"
        )

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_mapping(self, mock_get_sheet: MagicMock):
        """Tests successful sheet return response"""
        mock_get_sheet.return_value.to_json.return_value = self.example_sheet
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=7478444220698500
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        smart_sheet_response = client.get_sheet()
        mapper = ProtocolsMapper(
            smart_sheet_response=smart_sheet_response,
            input_id=(
                "Tetrahydrofuran and Dichloromethane Delipidation of a Whole"
                " Mouse Brain"
            ),
        )
        model_response = mapper.get_model_response()
        expected_models = [
            ProtocolInformation(
                protocol_type="Specimen Procedures",
                procedure_name="Delipidation",
                protocol_name=(
                    "Tetrahydrofuran and Dichloromethane Delipidation of a"
                    " Whole Mouse Brain"
                ),
                doi="dx.doi.org/10.17504/protocols.io.36wgqj1kxvk5/v1",
                version="1.0",
            ),
        ]
        self.assertEqual(expected_models, model_response.aind_models)
        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)

    @patch("smartsheet.sheets.Sheets.get_sheet")
    def test_mapping_empty_response(self, mock_get_sheet: MagicMock):
        """Tests empty return response"""
        mock_get_sheet.return_value.to_json.return_value = None
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=7478444220698500
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        smart_sheet_response = client.get_sheet()
        mapper = ProtocolsMapper(
            smart_sheet_response=smart_sheet_response, input_id="Protocol Name"
        )
        model_response = mapper.get_model_response()
        expected_models = []
        self.assertEqual(expected_models, model_response.aind_models)
        self.assertEqual(StatusCodes.NO_DATA_FOUND, model_response.status_code)

    @patch("smartsheet.sheets.Sheets.get_sheet")
    @patch("aind_metadata_service.models.ProtocolInformation.model_validate")
    def test_mapping_validation_error(
        self, mock_validate: MagicMock, mock_get_sheet: MagicMock
    ):
        """Tests validation error on Response model"""

        mock_validate.side_effect = ValidationError.from_exception_data(
            title="err", line_errors=[]
        )

        mock_get_sheet.return_value.to_json.return_value = self.example_sheet
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=7478444220698500
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        smart_sheet_response = client.get_sheet()
        mapper = ProtocolsMapper(
            smart_sheet_response=smart_sheet_response,
            input_id=self.nano_name,
        )
        model_response = mapper.get_model_response()
        expected_models = [
            ProtocolInformation.model_construct(
                protocol_type="Surgical Procedures",
                procedure_name="Injection Nanoject",
                protocol_name=self.nano_name,
                doi="dx.doi.org/10.17504/protocols.io.bp2l6nr7kgqe/v4",
                version=4.0,
            )
        ]
        # Additional validation is performed downstream, so we can just return
        # a model
        self.assertEqual(expected_models, model_response.aind_models)
        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)

    @patch("smartsheet.sheets.Sheets.get_sheet")
    @patch(
        "aind_metadata_service.smartsheet.protocols.mapping.ProtocolsMapper"
        "._get_protocol_list"
    )
    @patch("logging.error")
    def test_mapping_error(
        self,
        mock_log_error: MagicMock,
        mock_get_protocols_list: MagicMock,
        mock_get_sheet: MagicMock,
    ):
        """Tests mapping error"""

        mock_get_protocols_list.side_effect = MagicMock(
            side_effect=Exception("Mapping Error")
        )
        mock_get_sheet.return_value.to_json.return_value = self.example_sheet
        settings = SmartsheetSettings(
            access_token="abc-123", sheet_id=7478444220698500
        )
        client = SmartSheetClient(smartsheet_settings=settings)
        smart_sheet_response = client.get_sheet()
        mapper = ProtocolsMapper(
            smart_sheet_response=smart_sheet_response, input_id="Delipidation"
        )
        model_response = mapper.get_model_response()
        self.assertEqual(
            ModelResponse.internal_server_error_response().status_code,
            model_response.status_code,
        )
        mock_log_error.assert_has_calls(
            [
                call("Exception('Mapping Error')"),
            ]
        )

    def test_get_protocol_name(self):
        """Tests that protocol name is found from procedure type as expected"""
        nanoject_inj = NanojectInjection.model_construct()
        ionto_inj = IontophoresisInjection.model_construct()
        cran = Craniotomy.model_construct(
            protective_material=ProtectiveMaterial.DURAGEL
        )
        perfusion = Perfusion.model_construct()
        hf = Headframe.model_construct()
        self.assertEqual(
            self.protocols_integrator._get_protocol_name(nanoject_inj),
            ProtocolNames.INJECTION_NANOJECT.value,
        )
        self.assertEqual(
            self.protocols_integrator._get_protocol_name(ionto_inj),
            ProtocolNames.INJECTION_IONTOPHORESIS.value,
        )
        self.assertEqual(
            self.protocols_integrator._get_protocol_name(cran),
            ProtocolNames.DURAGEL_APPLICATION.value,
        )
        self.assertEqual(
            self.protocols_integrator._get_protocol_name(perfusion),
            ProtocolNames.PERFUSION.value,
        )
        self.assertIsNone(self.protocols_integrator._get_protocol_name(hf))

    def test_get_protocols_list(self):
        """Tests that protocols mapping is crated as expected"""
        nanoject_inj = NanojectInjection.model_construct()
        surgery = Surgery.model_construct(procedures=[nanoject_inj])
        procedures = Procedures.model_construct(subject_procedures=[surgery])
        response = ModelResponse(
            aind_models=[procedures], status_code=StatusCodes.DB_RESPONDED
        )
        protocols_list = self.protocols_integrator.get_protocols_list(response)
        expected_list = [
            ProtocolNames.SURGERY.value,
            ProtocolNames.INJECTION_NANOJECT.value,
        ]
        self.assertEqual(expected_list, protocols_list)

    def test_get_protocols_list_missing_procedures(self):
        """Tests that protocols mapping is crated as expected when objects
        are missing procedures."""
        surgery = Surgery.model_construct()
        procedures = Procedures.model_construct(subject_procedures=[surgery])
        response = ModelResponse(
            aind_models=[procedures], status_code=StatusCodes.DB_RESPONDED
        )
        protocols_list = self.protocols_integrator.get_protocols_list(response)
        expected_list = [
            ProtocolNames.SURGERY.value,
        ]
        self.assertEqual(expected_list, protocols_list)

    def test_integrate_protocols(self):
        """Tests that protocols are integrated into procedures
        response as expected"""
        nano_protocol = ProtocolInformation.model_construct(
            protocol_type="Surgical Procedures",
            procedure_name="Injection Nanoject",
            protocol_name=self.nano_name,
            doi="dx.doi.org/some/doi/1",
            version="1.0",
            protocol_collection=None,
        )
        surgery_protocol = ProtocolInformation.model_construct(
            protocol_type="Surgical Procedures",
            procedure_name="Surgery",
            protocol_name=self.surgery_name,
            doi="dx.doi.org/some/doi/2",
            version="1.0",
            protocol_collection=None,
        )
        protocols_response1 = ModelResponse(
            aind_models=[nano_protocol], status_code=StatusCodes.DB_RESPONDED
        )
        protocols_response2 = ModelResponse(
            aind_models=[surgery_protocol],
            status_code=StatusCodes.DB_RESPONDED,
        )
        protocols_mapping = {
            self.nano_name: protocols_response1.map_to_json_response(),
            self.surgery_name: protocols_response2.map_to_json_response(),
        }
        nanoject_inj = NanojectInjection.model_construct()
        surgery = Surgery.model_construct(
            experimenter_full_name="NSB-123", procedures=[nanoject_inj]
        )
        procedures_response = ModelResponse(
            aind_models=[
                Procedures(
                    subject_id="12345",
                    subject_procedures=[surgery],
                )
            ],
            status_code=StatusCodes.DB_RESPONDED,
        )
        merged_response = self.protocols_integrator.integrate_protocols(
            response=procedures_response, protocols_mapping=protocols_mapping
        )
        expected_surgery = Surgery.model_construct(
            protocol_id="dx.doi.org/some/doi/2",
            experimenter_full_name="NSB-123",
            procedures=[
                NanojectInjection.model_construct(
                    protocol_id="dx.doi.org/some/doi/1"
                )
            ],
        )
        expected_response = ModelResponse(
            aind_models=[
                Procedures(
                    subject_id="12345",
                    subject_procedures=[expected_surgery],
                )
            ],
            status_code=StatusCodes.DB_RESPONDED,
        )
        self.assertEqual(
            expected_response.aind_models, merged_response.aind_models
        )
        self.assertEqual(
            expected_response.status_code, merged_response.status_code
        )

    def test_integrate_protocols_missing_procedures(self):
        """Tests that protocols are integrated into procedures
        response as expected when objects are missing procedures attribute"""
        nano_protocol = ProtocolInformation.model_construct(
            protocol_type="Surgical Procedures",
            procedure_name="Injection Nanoject",
            protocol_name=self.nano_name,
            doi="dx.doi.org/some/doi/1",
            version="1.0",
            protocol_collection=None,
        )
        surgery_protocol = ProtocolInformation.model_construct(
            protocol_type="Surgical Procedures",
            procedure_name="Surgery",
            protocol_name=self.surgery_name,
            doi="dx.doi.org/some/doi/2",
            version="1.0",
            protocol_collection=None,
        )
        protocols_response1 = ModelResponse(
            aind_models=[nano_protocol], status_code=StatusCodes.DB_RESPONDED
        )
        protocols_response2 = ModelResponse(
            aind_models=[surgery_protocol],
            status_code=StatusCodes.DB_RESPONDED,
        )
        protocols_mapping = {
            self.nano_name: protocols_response1.map_to_json_response(),
            self.surgery_name: protocols_response2.map_to_json_response(),
        }
        surgery = Surgery.model_construct(experimenter_full_name="NSB-123")
        procedures_response = ModelResponse(
            aind_models=[
                Procedures(subject_id="12345", subject_procedures=[surgery])
            ],
            status_code=StatusCodes.DB_RESPONDED,
        )
        merged_response = self.protocols_integrator.integrate_protocols(
            response=procedures_response, protocols_mapping=protocols_mapping
        )
        expected_surgery = Surgery.model_construct(
            protocol_id="dx.doi.org/some/doi/2",
            experimenter_full_name="NSB-123",
        )
        expected_response = ModelResponse(
            aind_models=[
                Procedures(
                    subject_id="12345", subject_procedures=[expected_surgery]
                )
            ],
            status_code=StatusCodes.DB_RESPONDED,
        )
        self.assertEqual(
            expected_response.aind_models, merged_response.aind_models
        )
        self.assertEqual(
            expected_response.status_code, merged_response.status_code
        )

    def test_integrate_protocols_error(self):
        """Tests that injection materials are integrated into
        procedures response as expected"""
        protocols_response = ModelResponse(
            aind_models=[],
            status_code=StatusCodes.CONNECTION_ERROR,
        )
        protocols_mapping = {
            self.nano_name: protocols_response.map_to_json_response(),
            self.surgery_name: protocols_response.map_to_json_response(),
        }
        nanoject_inj = NanojectInjection.model_construct()
        surgery = Surgery.model_construct(
            experimenter_full_name="NSB-123", procedures=[nanoject_inj]
        )
        procedures_response = ModelResponse(
            aind_models=[
                Procedures(subject_id="12345", subject_procedures=[surgery])
            ],
            status_code=StatusCodes.DB_RESPONDED,
        )
        merged_response = self.protocols_integrator.integrate_protocols(
            response=procedures_response, protocols_mapping=protocols_mapping
        )
        self.assertEqual(merged_response.status_code, StatusCodes.MULTI_STATUS)

    def test_integrate_protocols_multi_status(self):
        """Tests that injection materials are integrated into
        procedures response as expected"""
        protocols_response = ModelResponse(
            aind_models=[],
            status_code=StatusCodes.NO_DATA_FOUND,
        )
        protocols_mapping = {
            self.nano_name: protocols_response.map_to_json_response(),
            self.surgery_name: protocols_response.map_to_json_response(),
        }
        nanoject_inj = NanojectInjection.model_construct()
        surgery = Surgery.model_construct(
            experimenter_full_name="NSB-123", procedures=[nanoject_inj]
        )
        procedures_response = ModelResponse(
            aind_models=[
                Procedures(subject_id="12345", subject_procedures=[surgery])
            ],
            status_code=StatusCodes.DB_RESPONDED,
        )
        merged_response = self.protocols_integrator.integrate_protocols(
            response=procedures_response, protocols_mapping=protocols_mapping
        )
        self.assertEqual(merged_response.status_code, StatusCodes.DB_RESPONDED)


if __name__ == "__main__":
    unittest.main()
