""""Tests response_handler module"""

import json
import unittest
from unittest.mock import MagicMock, patch

from aind_data_schema.core.subject import BreedingInfo, Species, Subject
from aind_data_schema_models.organizations import Organization
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from aind_metadata_service_server.response_handler import (
    ModelResponse,
    StatusCodes,
)


class TestResponseHandler(unittest.TestCase):
    """Tests JSON methods in Responses class"""

    @classmethod
    def setUpClass(cls) -> None:
        """Sets up class with pre-configured models"""
        cls.valid_subject = Subject(
            species=Species.MUS_MUSCULUS,
            source=Organization.AI,
            breeding_info=BreedingInfo(
                breeding_group="C57BL6J_OLD",
                maternal_id="107392",
                maternal_genotype="wt/wt",
                paternal_id="107384",
                paternal_genotype="Adora2a-Cre/wt",
            ),
            subject_id="639374",
            sex="Male",
            date_of_birth="2022-06-24",
            genotype="Pvalb-IRES-Cre/wt;RCL-somBiPoles_mCerulean-WPRE/wt",
        )
        cls.invalid_subject = Subject.model_construct()

    def test_valid_model(self):
        """Test model_response with valid model."""

        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED,
            aind_models=[self.valid_subject]
        )
        actual_json = model_response.map_to_json_response()

        model_json = jsonable_encoder(json.loads(
            self.valid_subject.model_dump_json())
        )
        expected_json = JSONResponse(
            status_code=200,
            content=(
                {
                    "message": "Valid Model.",
                    "data": model_json,
                }
            ),
        )

        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)
        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)

    def test_invalid_model(self):
        """Test model_response with invalid model."""
        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED,
            aind_models=[self.invalid_subject]
        )
        actual_json = model_response.map_to_json_response()

        validation_error = None
        try:
            self.invalid_subject.__class__.model_validate(
                self.invalid_subject.model_dump()
            )
        except ValidationError as e:
            validation_error = repr(e)

        model_json = jsonable_encoder(self.invalid_subject)
        expected_json = JSONResponse(
            status_code=406,
            content=(
                {
                    "message": f"Validation Errors: {validation_error}",
                    "data": model_json,
                }
            ),
        )
        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)
        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)

    @patch("aind_metadata_service_server.response_handler.json.loads")
    @patch(
        "aind_metadata_service_server.response_handler.Subject.model_validate"
    )
    def test_key_error(self, mock_model_validate, mock_json_loads):
        """Test model_response with valid model."""
        key_error = KeyError("Mocked Key Error")
        mock_model_validate.side_effect = key_error
        mock_json_loads.return_value = {"invalid_key": "value"}
        aind_model = MagicMock(spec=Subject)
        aind_model.model_dump.return_value = "{}"
        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED, aind_models=[aind_model]
        )
        actual_json = model_response.map_to_json_response()
        expected_json = JSONResponse(
            status_code=406,
            content=(
                {
                    "message": f"Validation Errors: KeyError({key_error})",
                    "data": {"invalid_key": "value"},
                }
            ),
        )
        self.assertEqual(
            actual_json.status_code, StatusCodes.INVALID_DATA.value
        )
        self.assertEqual(actual_json.body, expected_json.body)

    def test_no_validation(self):
        """Test model_response when validation is turned off."""
        model = Subject.model_construct()
        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED, aind_models=[model]
        )
        actual_json = model_response.map_to_json_response(validate=False)
        model_json = jsonable_encoder(model)
        expected_json = JSONResponse(
            status_code=422,
            content=(
                {
                    "message": "Valid Request Format. "
                    "Models have not been validated.",
                    "data": model_json,
                }
            ),
        )

        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)
        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)

    def test_multiple_items_response(self):
        """Test multiple item response with validation."""
        models = [self.valid_subject, self.valid_subject]
        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED, aind_models=models
        )
        actual_json = model_response.map_to_json_response()

        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)
        self.assertEqual(300, actual_json.status_code)
        self.assertIn("Multiple Items Found", str(actual_json.body))

    def test_multiple_items_response_no_validation(self):
        """Test multiple item response"""
        models = [self.valid_subject, self.valid_subject]
        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED, aind_models=models
        )
        actual_json = model_response.map_to_json_response(validate=False)

        models_json = [
            jsonable_encoder(json.loads(model.model_dump_json()))
            for model in models
        ]
        expected_json = JSONResponse(
            status_code=300,
            content=(
                {
                    "message": "Multiple Items Found."
                    " Models have not been validated.",
                    "data": models_json,
                }
            ),
        )

        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)
        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)

    def test_nodata_error(self):
        """Test no data error response"""
        model_response = ModelResponse(
            status_code=StatusCodes.DB_RESPONDED, aind_models=[]
        )
        actual_json = model_response.map_to_json_response()

        expected_json = JSONResponse(
            status_code=404,
            content=(
                {
                    "message": "No Data Found.",
                    "data": None,
                }
            ),
        )
        self.assertEqual(StatusCodes.DB_RESPONDED, model_response.status_code)
        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)

    def test_connection_error(self):
        """Test connection error response"""
        model_response = ModelResponse.connection_error_response()
        actual_json = model_response.map_to_json_response()

        expected_json = JSONResponse(
            status_code=503,
            content=(
                {
                    "message": "Connection Error.",
                    "data": None,
                }
            ),
        )
        self.assertEqual(
            StatusCodes.CONNECTION_ERROR, model_response.status_code
        )
        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)

    def test_internal_error(self):
        """Test internal error response"""
        model_response = ModelResponse.internal_server_error_response()
        actual_json = model_response.map_to_json_response()

        expected_json = JSONResponse(
            status_code=500,
            content=(
                {
                    "message": "Internal Server Error.",
                    "data": None,
                }
            ),
        )
        self.assertEqual(
            StatusCodes.INTERNAL_SERVER_ERROR, model_response.status_code
        )
        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)

    def test_bad_request_error(self):
        """Test bad request error response"""
        model_response = ModelResponse.bad_request_error_response()
        actual_json = model_response.map_to_json_response()
        expected_json = JSONResponse(
            status_code=400,
            content=(
                {
                    "message": "Bad Request.",
                    "data": None,
                }
            ),
        )
        self.assertEqual(StatusCodes.BAD_REQUEST, model_response.status_code)
        self.assertEqual(expected_json.status_code, actual_json.status_code)
        self.assertEqual(expected_json.body, actual_json.body)


if __name__ == "__main__":
    unittest.main()
