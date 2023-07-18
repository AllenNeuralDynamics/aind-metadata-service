""""Tests response_handler module"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from aind_data_schema.procedures import Procedures
from aind_data_schema.subject import Species, Subject
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import validate_model

from aind_metadata_service.response_handler import Responses

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
DIR_MAP = TEST_DIR / "resources" / "json_responses"

SP_VALID_RESPONSE_PATH = DIR_MAP / "mapped_sp_procedure.json"
LAS_VALID_RESPONSE_PATH = DIR_MAP / "mapped_las_procedure.json"
COMBINED_VALID_PATH = DIR_MAP / "combined.json"

SP_INVALID_RESPONSE_PATH = DIR_MAP / "mapped_sp_procedure_invalid.json"
LAS_INVALID_RESPONSE_PATH = DIR_MAP / "mapped_las_procedure_invalid.json"
COMBINED_INVALID_PATH = DIR_MAP / "combined_invalid.json"

with open(SP_VALID_RESPONSE_PATH) as f:
    sp_valid_subject_procedures = json.load(f)

with open(LAS_VALID_RESPONSE_PATH) as f:
    las_valid_subject_procedures = json.load(f)

with open(COMBINED_VALID_PATH) as f:
    combined_valid_procedures = json.load(f)

with open(SP_INVALID_RESPONSE_PATH) as f:
    sp_invalid_subject_procedures = json.load(f)

with open(LAS_INVALID_RESPONSE_PATH) as f:
    las_invalid_subject_procedures = json.load(f)

with open(COMBINED_INVALID_PATH) as f:
    combined_invalid_procedures = json.load(f)

sp_valid_model = Procedures.construct(
    subject_id="115977",
    subject_procedures=sp_valid_subject_procedures["data"]["subject_procedures"],
)
lb_valid_model = Procedures.construct(
    subject_id="115977",
    subject_procedures=las_valid_subject_procedures["data"]["subject_procedures"],
)
sp_invalid_model = Procedures.construct(
    subject_id="115977",
    subject_procedures=sp_invalid_subject_procedures["data"]["subject_procedures"],
)
lb_invalid_model = Procedures.construct(
    subject_id="115977",
    subject_procedures=las_invalid_subject_procedures["data"]["subject_procedures"],
)
class TestResponseHandler(unittest.TestCase):
    """Tests JSON methods in Responses class"""

    def test_valid_model(self):
        """Test model_response with valid model."""

        model = Subject(
            species=Species.MUS_MUSCULUS,
            subject_id="639374",
            sex="Male",
            date_of_birth="2022-06-24",
            genotype="Pvalb-IRES-Cre/wt;RCL-somBiPoles_mCerulean-WPRE/wt",
        )
        model_response = Responses.model_response(model)
        actual_json = Responses.convert_response_to_json(*model_response)

        model_json = jsonable_encoder(json.loads(model.json()))
        expected_json = JSONResponse(
            status_code=200,
            content=(
                {
                    "message": "Valid Model.",
                    "data": model_json,
                }
            ),
        )

        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)

    def test_invalid_model(self):
        """Test model_response with invalid model."""
        model = Subject.construct()
        model_response = Responses.model_response(model)
        actual_json = Responses.convert_response_to_json(*model_response)

        *_, validation_error = validate_model(model.__class__, model.__dict__)
        model_json = jsonable_encoder(model)
        expected_json = JSONResponse(
            status_code=406,
            content=(
                {
                    "message": f"Validation Errors: {validation_error}",
                    "data": model_json,
                }
            ),
        )

        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)

    def test_connection_error(self):
        """Test connection error response"""
        response = Responses.connection_error_response()
        actual_json = Responses.convert_response_to_json(*response)
        expected_json = JSONResponse(
            status_code=503,
            content=(
                {
                    "message": "Error Connecting to Internal Server.",
                    "data": None,
                }
            ),
        )
        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)

    def test_combine_internal_error_responses(self):
        """Tests that error responses are combined as expected"""
        response1 = Responses.internal_server_error_response()
        response2 = Responses.internal_server_error_response()
        combined_response = Responses.combine_procedure_responses(
            lb_response=response1, sp_response=response2
        )
        actual_json = Responses.convert_response_to_json(*combined_response)
        expected_json = Responses.convert_response_to_json(
            *Responses.internal_server_error_response(),
            "Internal Server Error.",
        )
        self.assertEqual(expected_json.body, actual_json.body)
        self.assertEqual(500, actual_json.status_code)

    def test_combine_connection_error_responses(self):
        """Tests that error responses are combined as expected"""
        response1 = Responses.connection_error_response()
        response2 = Responses.connection_error_response()
        combined_response = Responses.combine_procedure_responses(
            lb_response=response1, sp_response=response2
        )
        actual_json = Responses.convert_response_to_json(*combined_response)
        expected_json = Responses.convert_response_to_json(
            *Responses.connection_error_response(),
            "Error Connecting to Internal Server.",
        )
        self.assertEqual(expected_json.body, actual_json.body)
        self.assertEqual(503, actual_json.status_code)

    def test_combine_no_data_error_responses(self):
        """Tests that error responses are combined as expected"""
        response1 = Responses.no_data_found_response()
        response2 = Responses.no_data_found_response()
        combined_response = Responses.combine_procedure_responses(
            lb_response=response1, sp_response=response2
        )
        actual_json = Responses.convert_response_to_json(*combined_response)
        expected_json = Responses.convert_response_to_json(
            *Responses.no_data_found_response(), "No Data Found."
        )
        self.assertEqual(expected_json.body, actual_json.body)
        self.assertEqual(404, actual_json.status_code)

    def test_combine_valid_no_data_error_responses(self):
        """Tests that error responses are combined as expected"""
        response1 = Responses.no_data_found_response()
        response2 = Responses.model_response(lb_valid_model)
        response3 = Responses.model_response(sp_valid_model)
        combined_response_1 = Responses.combine_procedure_responses(
            lb_response=response2, sp_response=response1
        )
        combined_json_1 = Responses.convert_response_to_json(
            *combined_response_1
        )
        expected_json_1 = JSONResponse(las_valid_subject_procedures)
        self.assertEqual(expected_json_1.body, combined_json_1.body)
        self.assertEqual(200, combined_json_1.status_code)

        combined_response_2 = Responses.combine_procedure_responses(
            lb_response=response1, sp_response=response3
        )
        combined_json_2 = Responses.convert_response_to_json(
            *combined_response_2
        )
        expected_json_2 = JSONResponse(sp_valid_subject_procedures)
        self.assertEqual(expected_json_2.body, combined_json_2.body)
        self.assertEqual(200, combined_json_2.status_code)

    def test_combine_valid_responses(self):
        """Tests that valid responses are combined as expected"""
        response1 = Responses.model_response(lb_valid_model)
        response2 = Responses.model_response(sp_valid_model)
        response = Responses.combine_procedure_responses(
            lb_response=response1, sp_response=response2
        )
        actual_json = Responses.convert_response_to_json(*response)
        expected_json = JSONResponse(combined_valid_procedures)
        self.assertEqual(expected_json.body, actual_json.body)
        self.assertEqual(200, actual_json.status_code)

    def test_combine_invalid_responses(self):
        """Tests that invalid responses are combined as expected"""
        model1 = lb_invalid_model
        *_, validation_error_1 = validate_model(
            model1.__class__, model1.__dict__
        )
        model2 = sp_invalid_model
        *_, validation_error_2 = validate_model(
            model2.__class__, model2.__dict__
        )
        response1 = Responses.model_response(model1)
        response2 = Responses.model_response(model2)
        response = Responses.combine_procedure_responses(
            lb_response=response1, sp_response=response2
        )
        actual_json = Responses.convert_response_to_json(*response)
        expected_json = JSONResponse(
            status_code=406,
            content=(
                {
                    "message": f"Message 1: "
                    f"Validation Errors: {str(validation_error_1)},"
                    f"Message 2: "
                    f"Validation Errors: {str(validation_error_2)}",
                    "data": combined_invalid_procedures["data"],
                }
            ),
        )
        self.assertEqual(expected_json.body, actual_json.body)
        self.assertEqual(expected_json.status_code, actual_json.status_code)

    def test_combine_valid_invalid_responses(self):
        """Tests that valid and invalid response are combined as expected.
        (This unit test only works when the lb_model is invalid,
        because the simple invalid model created solely for testing sake doesn't have a subject_id field,
        and the combine_procedure_responses uses the sp_response as basis of combination. However,
        this is still a valid test for combine function since actual models will always have a subject_id field. )
        """
        model = Procedures.construct()
        response1 = Responses.model_response(model)
        response2 = Responses.model_response(sp_valid_model)
        *_, validation_error = validate_model(model.__class__, model.__dict__)
        response = Responses.combine_procedure_responses(
            lb_response=response1, sp_response=response2
        )
        actual_json = Responses.convert_response_to_json(*response)
        expected_json = JSONResponse(
            status_code=207,
            content=(
                {
                    "message": f"Message 1: Validation Errors: {str(validation_error)},"
                    f"Message 2: Valid Model.",
                    "data": sp_subject_procedures["data"],
                }
            ),
        )
        self.assertEqual(expected_json.body, actual_json.body)
        self.assertEqual(expected_json.status_code, actual_json.status_code)

    def test_combine_valid_error_responses(self):
        """Tests that error responses are combined as expected"""
        response1 = Responses.connection_error_response()
        response2 = Responses.model_response(sp_valid_model)
        combined_response_1 = Responses.combine_procedure_responses(
            lb_response=response1, sp_response=response2
        )
        actual_json_1 = Responses.convert_response_to_json(
            *combined_response_1
        )
        expected_json_1 = JSONResponse(
            status_code=207,
            content=(
                {
                    "message": "Message 1: Valid Model., "
                    "Message 2: Error Connecting to Internal Server.",
                    "data": sp_valid_subject_procedures["data"],
                }
            ),
        )
        self.assertEqual(expected_json_1.body, actual_json_1.body)
        self.assertEqual(
            expected_json_1.status_code, actual_json_1.status_code
        )

        response3 = Responses.model_response(sp_model)
        combined_response_2 = Responses.combine_procedure_responses(
            lb_response=response3, sp_response=response1
        )
        actual_json_2 = Responses.convert_response_to_json(
            *combined_response_2
        )
        expected_json_2 = JSONResponse(
            status_code=207,
            content=(
                {
                    "message": "Message 1: "
                    "Error Connecting to Internal Server., "
                    "Message 2: Valid Model.",
                    "data": las_valid_subject_procedures["data"],
                }
            ),
        )
        self.assertEqual(expected_json_2.body, actual_json_2.body)
        self.assertEqual(
            expected_json_2.status_code, actual_json_2.status_code
        )

    @patch("json.loads")
    @patch("logging.error")
    def test_error_combined_response(
        self, mock_log: MagicMock, mock_json_error: MagicMock
    ):
        """Tests internal server error caught and logged correctly."""
        response1 = Responses.model_response(lb_model)
        response2 = Responses.model_response(sp_model)

        mock_json_error.side_effect = Mock(side_effect=KeyError)

        combined_response = Responses.combine_procedure_responses(
            lb_response=response1, sp_response=response2
        )
        actual_json = Responses.convert_response_to_json(*combined_response)
        expected_json = Responses.convert_response_to_json(
            Responses.internal_server_error_response()
        )
        mock_log.assert_called_once_with("KeyError()")
        self.assertEqual(500, expected_json.status_code)
        self.assertEqual(actual_json.body, expected_json.body)


if __name__ == "__main__":
    unittest.main()
