""""Tests response_handler module"""

import unittest

from aind_data_schema.subject import Subject
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import validate_model

from aind_metadata_service.response_handler import Responses


class TestResponseHandler(unittest.TestCase):
    """Tests methods in Responses class"""

    def test_valid_model(self):
        """Test model_response with valid model."""

        model = Subject(
            species="Mus musculus",
            subject_id="639374",
            sex="Male",
            date_of_birth="2022-06-24",
            genotype="Pvalb-IRES-Cre/wt;RCL-somBiPoles_mCerulean-WPRE/wt",
        )
        response = Responses.model_response(model)
        model_json = jsonable_encoder(model)
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


if __name__ == "__main__":
    unittest.main()
