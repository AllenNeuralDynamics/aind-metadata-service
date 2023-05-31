""""Tests response_handler module"""

import json
import os
import unittest
from pathlib import Path

from aind_data_schema.procedures import Procedures
from aind_data_schema.subject import Species, Subject
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import validate_model

from aind_metadata_service.response_handler import Responses

TEST_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
DIR_MAP = TEST_DIR / "resources" / "json_responses"

SP_RESPONSE_PATH = DIR_MAP / "mapped_sp_procedure.json"
LAS_RESPONSE_PATH = DIR_MAP / "mapped_las_procedure.json"
COMBINED_PATH = DIR_MAP / "combined.json"

with open(SP_RESPONSE_PATH) as f:
    sp_subject_procedures = json.load(f)

with open(LAS_RESPONSE_PATH) as f:
    las_subject_procedures = json.load(f)

with open(COMBINED_PATH) as f:
    combined_procedures = json.load(f)


class TestResponseHandler(unittest.TestCase):
    """Tests methods in Responses class"""

    def test_valid_model(self):
        """Test model_response with valid model."""

        model = Subject(
            species=Species.MUS_MUSCULUS,
            subject_id="639374",
            sex="Male",
            date_of_birth="2022-06-24",
            genotype="Pvalb-IRES-Cre/wt;RCL-somBiPoles_mCerulean-WPRE/wt",
        )
        response = Responses.model_response(model)
        model_json = jsonable_encoder(json.loads(model.json()))
        expected_response = JSONResponse(
            status_code=200,
            content=(
                {
                    "message": "Valid Model.",
                    "data": model_json,
                }
            ),
        )

        self.assertEqual(expected_response.status_code, response.status_code)
        self.assertEqual(expected_response.body, response.body)

    def test_invalid_model(self):
        """Test model_response with invalid model."""
        model = Subject.construct()
        response = Responses.model_response(model)
        *_, validation_error = validate_model(model.__class__, model.__dict__)
        model_json = jsonable_encoder(model)
        expected_response = JSONResponse(
            status_code=406,
            content=(
                {
                    "message": f"Validation Errors: {validation_error}",
                    "data": model_json,
                }
            ),
        )

        self.assertEqual(expected_response.status_code, response.status_code)
        self.assertEqual(expected_response.body, response.body)

    def test_connection_error(self):
        """Test connection error response"""
        response = Responses.connection_error_response()
        expected_response = JSONResponse(
            status_code=503,
            content=(
                {
                    "message": "Error Connecting to Internal Server.",
                    "data": None,
                }
            ),
        )
        self.assertEqual(expected_response.status_code, response.status_code)
        self.assertEqual(expected_response.body, response.body)

    def test_combine_internal_error_responses(self):
        """Tests that error responses are combined as expected"""
        response1 = Responses.internal_server_error_response()
        response2 = Responses.internal_server_error_response()
        response = Responses.combine_procedure_responses(
            lb_response=response1, sp_response=response2
        )
        expected_response = Responses.internal_server_error_response()
        self.assertEqual(response.body, expected_response.body)
        self.assertEqual(response.status_code, 500)

    def test_combine_connection_error_responses(self):
        """Tests that error responses are combined as expected"""
        response1 = Responses.connection_error_response()
        response2 = Responses.connection_error_response()
        response = Responses.combine_procedure_responses(
            lb_response=response1, sp_response=response2
        )
        expected_response = Responses.connection_error_response()
        self.assertEqual(response.body, expected_response.body)
        self.assertEqual(response.status_code, 503)

    def test_combine_no_data_error_responses(self):
        """Tests that error responses are combined as expected"""
        response1 = Responses.no_data_found_response()
        response2 = Responses.no_data_found_response()
        response = Responses.combine_procedure_responses(
            lb_response=response1, sp_response=response2
        )
        expected_response = Responses.no_data_found_response()
        self.assertEqual(response.body, expected_response.body)
        self.assertEqual(response.status_code, 404)

    def test_combine_valid_no_data_error_responses(self):
        """Tests that error responses are combined as expected"""
        response1 = Responses.no_data_found_response()
        response2 = JSONResponse(las_subject_procedures)
        response3 = JSONResponse(sp_subject_procedures)
        combined_response_1 = Responses.combine_procedure_responses(
            lb_response=response2, sp_response=response1
        )
        expected_response_1 = JSONResponse(las_subject_procedures)
        self.assertEqual(combined_response_1.body, expected_response_1.body)
        self.assertEqual(combined_response_1.status_code, 200)

        combined_response_2 = Responses.combine_procedure_responses(
            lb_response=response1, sp_response=response3
        )
        expected_response_2 = JSONResponse(sp_subject_procedures)
        self.assertEqual(combined_response_2.body, expected_response_2.body)
        self.assertEqual(combined_response_2.status_code, 200)

    def test_combine_valid_responses(self):
        """Tests that valid responses are combined as expected"""
        response1 = JSONResponse(las_subject_procedures)
        response2 = JSONResponse(sp_subject_procedures)
        response = Responses.combine_procedure_responses(
            lb_response=response1, sp_response=response2
        )
        expected_response = JSONResponse(combined_procedures)
        self.assertEqual(expected_response.body, response.body)
        self.assertEqual(200, response.status_code)

    def test_combine_invalid_responses(self):
        """Tests that invalid responses are combined as expected"""
        model1 = Procedures.construct(
            subject_id="115977",
            extra_field=None,
            subject_procedures=sp_subject_procedures["data"][
                "subject_procedures"
            ],
        )
        *_, validation_error_1 = validate_model(
            model1.__class__, model1.__dict__
        )
        model2 = Procedures.construct(
            subject_id="115977",
            subject_procedures=las_subject_procedures["data"][
                "subject_procedures"
            ],
        )
        *_, validation_error_2 = validate_model(
            model2.__class__, model2.__dict__
        )
        response1 = Responses.model_response(model1)
        response2 = Responses.model_response(model2)
        response = Responses.combine_procedure_responses(
            lb_response=response2, sp_response=response1
        )
        expected_response = JSONResponse(
            status_code=406,
            content=(
                {
                    "message": f"Message 1: "
                    f"Validation Errors: {str(validation_error_1)}, "
                    f"Message 2: "
                    f"Validation Errors: {str(validation_error_2)}",
                    "data": combined_procedures["data"],
                }
            ),
        )
        self.assertEqual(response.body, expected_response.body)
        self.assertEqual(response.status_code, expected_response.status_code)

    def test_combine_valid_invalid_responses(self):
        """Tests that valid and invalid response are combined as expected"""
        model = Procedures.construct()
        response1 = JSONResponse(sp_subject_procedures)
        response2 = Responses.model_response(model)
        *_, validation_error = validate_model(model.__class__, model.__dict__)
        response = Responses.combine_procedure_responses(
            lb_response=response2, sp_response=response1
        )
        expected_response = JSONResponse(
            status_code=207,
            content=(
                {
                    "message": f"Message 1: Valid Model., "
                    f"Message 2: Validation Errors: {str(validation_error)}",
                    "data": sp_subject_procedures["data"],
                }
            ),
        )
        self.assertEqual(response.body, expected_response.body)
        self.assertEqual(response.status_code, expected_response.status_code)

    def test_combine_valid_error_responses(self):
        """Tests that error responses are combined as expected"""
        response1 = Responses.connection_error_response()
        response2 = JSONResponse(sp_subject_procedures)
        combined_response_1 = Responses.combine_procedure_responses(
            lb_response=response1, sp_response=response2
        )
        expected_response_1 = JSONResponse(
            status_code=207,
            content=(
                {
                    "message": "Message 1: Valid Model., "
                    "Message 2: Error Connecting to Internal Server.",
                    "data": sp_subject_procedures["data"],
                }
            ),
        )
        self.assertEqual(combined_response_1.body, expected_response_1.body)
        self.assertEqual(
            combined_response_1.status_code, expected_response_1.status_code
        )

        response3 = JSONResponse(las_subject_procedures)
        combined_response_2 = Responses.combine_procedure_responses(
            lb_response=response3, sp_response=response1
        )
        expected_response_2 = JSONResponse(
            status_code=207,
            content=(
                {
                    "message": "Message 1: "
                    "Error Connecting to Internal Server., "
                    "Message 2: Valid Model.",
                    "data": las_subject_procedures["data"],
                }
            ),
        )
        self.assertEqual(combined_response_2.body, expected_response_2.body)
        self.assertEqual(
            combined_response_2.status_code, expected_response_2.status_code
        )


if __name__ == "__main__":
    unittest.main()
